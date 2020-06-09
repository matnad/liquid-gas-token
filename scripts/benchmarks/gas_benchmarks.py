import json
from pathlib import Path

from brownie import *
from brownie.utils import color

DEADLINE = 99999999999
TEST_SET = [1, 15, 32, 71]
BENCHMARK_FILE = Path(__file__).parent.absolute().joinpath(Path("benchmarks.json"))


class MissedBenchmark(Exception):
    pass


def color_string(string, col):
    return f"{color(col)}{string}{color}"


def main(update_benchmarks: str = "never"):
    # Set up LGT contract
    rpc.reset()
    with BENCHMARK_FILE.open() as fp:
        benchmarks = json.load(fp)

    lgt_deployer = accounts.add("0x7d4cbcfd42fe584226a17f385f734b046090f3e9d9fd95b2e10ef53acbbc39e2")

    accounts[9].transfer("0x000000000049091f98692b2460500b6d133ae31f", "0.001 ether")
    lgt = lgt_deployer.deploy(LiquidGasToken)
    lgt.mint(80, {'from': accounts[0]})
    lgt.addLiquidity(1, 50, DEADLINE, {'from': accounts[0], 'value': "0.049 ether"})
    lgt.mint(80, {'from': accounts[1]})
    lgt.addLiquidity(1, 50, DEADLINE, {'from': accounts[1], 'value': "0.049 ether"})

    rpc.snapshot()

    # Run benchmarks
    results = benchmarks.copy()
    for category in benchmarks:
        for function in benchmarks[category]:
            gas_used = []
            for tokens in TEST_SET:
                rpc.revert()
                args = [
                    accounts[0] if arg == 'account' else arg
                    for arg in benchmarks[category][function]["args"]
                ]
                tx_args = {'from': accounts[0]}
                if "value" in benchmarks[category][function]:
                    try:
                        tx_args["value"] = Wei(benchmarks[category][function]["value"])
                    except TypeError:
                        tx_args["value"] = getattr(
                            lgt,
                            benchmarks[category][function]["value"]
                        )(tokens)
                tx = getattr(lgt, function)(tokens, *args, tx_args)
                gas_used.append(tx.gas_used)
            results[category][function]["gas_used"] = gas_used

    # Process results
    total_improvement = 0
    for category in benchmarks:
        for function in benchmarks[category]:
            mark = benchmarks[category][function]["gas_used"]
            score = results[category][function]["gas_used"]
            for i in range(len(TEST_SET)):
                improvement = mark[i] - score[i]
                total_improvement += improvement
                out_string = f"{color_string(function, 'bright magenta')}({TEST_SET[i]}) " \
                             f"{str(score[i]).ljust(7)} gas used: "
                out_string = out_string.rjust(60)
                if improvement > 0:
                    out_string += color_string(f"[ BENCHMARK IMPROVED BY {improvement} ]", "dark green")
                elif improvement < 0:
                    out_string += color_string(f"[ BENCHMARK MISSED BY {improvement} ]", "dark red")
                else:
                    out_string += color_string("[ BENCHMARK MATCHED ]", "bright yellow")
                print(out_string)

    ti_col = "bright yellow"
    if total_improvement > 0:
        ti_col = "dark green"
    elif total_improvement < 0:
        ti_col = "dark red"
    print(f"\n     TOTAL IMPROVEMENT: {color_string(total_improvement, ti_col)}")

    # Update Benchmarks
    if (
            update_benchmarks == "always"
            or (update_benchmarks == "on_improvement" and total_improvement > 0)
    ):
        print("\n     Updating Benchmarks...")
        with BENCHMARK_FILE.open("w") as fp:
            json.dump(results, fp, sort_keys=True, indent=2, default=sorted)

    network.disconnect()
    # Raise if benchmarks missed
    if total_improvement < 0:
        raise MissedBenchmark(f"Benchmark missed by {total_improvement}")
