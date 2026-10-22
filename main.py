"""CRC 시뮬레이션: 교재 예제 재현 + 오류 주입 후 검출률 측정."""
import random

from crc import GENERATORS, check, encode, mod2_div, poly_to_str, print_division
from plot_crc import plot_results

TRIALS = 20000     # 오류 유형별 시뮬레이션 횟수
DATA_BITS = 64     # 시뮬레이션용 데이터 길이 m
SEED = 2026


def flip(bits, positions):
    """지정한 위치의 비트를 반전 (전송 중 오류 발생)."""
    b = list(bits)
    for p in positions:
        b[p] = "1" if b[p] == "0" else "0"
    return "".join(b)


def random_bits(n):
    return "".join(random.choice("01") for _ in range(n))


# ---------------------------------------------------------------- 오류 패턴
def err_single(length, n):
    return [random.randrange(length)]


def err_double(length, n):
    return random.sample(range(length), 2)


def err_odd(length, n):
    k = random.choice([1, 3, 5, 7])
    return random.sample(range(length), k)


def burst(length, blen):
    """길이 blen인 버스트 오류: 양 끝 비트는 반드시 반전, 가운데는 무작위."""
    start = random.randrange(length - blen + 1)
    positions = [start, start + blen - 1] if blen > 1 else [start]
    positions += [start + i for i in range(1, blen - 1) if random.random() < 0.5]
    return positions


def err_burst_le_n(length, n):
    return burst(length, random.randint(1, n))


def err_burst_n1(length, n):
    return burst(length, n + 1)


def err_burst_long(length, n):
    return burst(length, random.randint(n + 2, length))


ERROR_TYPES = [
    ("1비트 오류", err_single),
    ("2비트 오류", err_double),
    ("홀수 개 비트 오류", err_odd),
    ("버스트 길이 <= n", err_burst_le_n),
    ("버스트 길이 = n+1", err_burst_n1),
    ("버스트 길이 > n+1", err_burst_long),
]


# ---------------------------------------------------------------- 1. 교재 예제
def textbook_example():
    print("=" * 70)
    print("1. 교재 예제 재현 [그림 4-20]")
    print("=" * 70)
    g, data = "100101", "101101001"
    print(f"생성 다항식 G(x) = {poly_to_str(g)}  ({g})")
    print(f"전송 데이터 M(x) = {data}\n")
    remainder = print_division(data, g)
    codeword = encode(data, g)
    print(f"\n체크섬      : {remainder}   (교재 정답 00010 -> {'일치' if remainder == '00010' else '불일치'})")
    print(f"송신 데이터 : {codeword}   (교재 정답 10110100100010 -> "
          f"{'일치' if codeword == '10110100100010' else '불일치'})")


# ---------------------------------------------------------------- 2. 송수신 시연
def transmission_demo():
    print("\n" + "=" * 70)
    print("2. 송신 -> 전송 선로 -> 수신 시연")
    print("=" * 70)
    g, data = "100101", "101101001"
    codeword = encode(data, g)
    cases = [
        ("오류 없음", codeword),
        ("3번 비트 반전", flip(codeword, [3])),
        ("0,5번 비트 반전", flip(codeword, [0, 5])),
        ("G(x) 배수 오류(검출 실패 예)", flip(codeword, [i for i, b in enumerate("100101") if b == "1"])),
    ]
    print(f"{'상황':<28}{'수신 데이터':<18}{'나머지':<8}판정")
    for name, received in cases:
        _, rem, _ = mod2_div(received, g)
        verdict = "정상 수신" if check(received, g) else "오류 검출!"
        print(f"{name:<28}{received:<18}{rem:<8}{verdict}")
    print("※ 오류 패턴 자체가 G(x)로 나누어떨어지면 CRC는 오류를 검출하지 못한다.")


# ---------------------------------------------------------------- 3. 몬테카를로 시뮬레이션
def simulate():
    print("\n" + "=" * 70)
    print(f"3. 오류 검출률 시뮬레이션 (데이터 {DATA_BITS}비트, 유형별 {TRIALS}회)")
    print("=" * 70)
    random.seed(SEED)
    results = {}
    for gname, g in GENERATORS.items():
        n = len(g) - 1
        print(f"\n[{gname}]  G(x) = {poly_to_str(g)}  (체크섬 {n}비트)")
        print(f"  {'오류 유형':<18}{'검출':>8}{'미검출':>8}{'검출률':>11}")
        results[gname] = {}
        for ename, pattern in ERROR_TYPES:
            detected = 0
            for _ in range(TRIALS):
                codeword = encode(random_bits(DATA_BITS), g)
                received = flip(codeword, pattern(len(codeword), n))
                if not check(received, g):
                    detected += 1
            rate = detected / TRIALS * 100
            results[gname][ename] = rate
            print(f"  {ename:<18}{detected:>8}{TRIALS - detected:>8}{rate:>10.3f}%")
    return results


if __name__ == "__main__":
    textbook_example()
    transmission_demo()
    results = simulate()
    plot_results(results, GENERATORS, TRIALS)
