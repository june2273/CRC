"""CRC(Cyclic Redundancy Code, 다항 코드) 구현.

교재 [그림 4-19]의 절차를 그대로 따른다.
  1. m비트 데이터 M(x) 뒤에 n개의 0을 붙인다 (n = 생성 다항식 G(x)의 차수).
  2. 모듈로-2 나눗셈(XOR)으로 나머지(체크섬, n비트)를 구한다.
  3. 원래 데이터 뒤에 체크섬을 붙여 m+n비트를 전송한다.
  4. 수신 측은 받은 m+n비트를 G(x)로 나누어 나머지가 0이면 정상, 아니면 오류로 판단한다.
"""

# 국제 표준 생성 다항식 (교재 36쪽) + 교재 예제 다항식
GENERATORS = {
    "교재 예제 (x^5+x^2+1)": "100101",
    "CRC-12": "1100000001111",       # x^12 + x^11 + x^3 + x^2 + x + 1
    "CRC-16": "11000000000000101",   # x^16 + x^15 + x^2 + 1
    "CRC-CCITT": "10001000000100001",  # x^16 + x^12 + x^5 + 1
}


def poly_to_str(generator):
    """'100101' -> 'x^5 + x^2 + 1'"""
    n = len(generator) - 1
    terms = []
    for i, bit in enumerate(generator):
        if bit == "1":
            power = n - i
            terms.append("1" if power == 0 else "x" if power == 1 else f"x^{power}")
    return " + ".join(terms)


def xor(a, b):
    """같은 길이의 비트 문자열에 대한 모듈로-2 덧셈/뺄셈 (= XOR)."""
    return "".join("0" if x == y else "1" for x, y in zip(a, b))


def mod2_div(dividend, generator, trace=False):
    """모듈로-2 나눗셈. (몫, 나머지, 계산 과정)을 반환한다.

    교재 [그림 4-20]처럼 한 자리씩 내려가며, 현재 맨 앞 비트가 1이면 G(x)를,
    0이면 000...0을 XOR 한다.
    """
    k = len(generator)
    current = dividend[:k]
    quotient = ""
    steps = []
    for i in range(k, len(dividend) + 1):
        divisor = generator if current[0] == "1" else "0" * k
        quotient += current[0]
        result = xor(current, divisor)
        if trace:
            steps.append((i - k, current, divisor, result))
        # 맨 앞 비트(항상 0)를 버리고 다음 비트를 내려온다
        current = result[1:] + (dividend[i] if i < len(dividend) else "")
    remainder = current
    return quotient, remainder, steps


def compute_checksum(data, generator):
    """송신 측: 데이터 뒤에 n개의 0을 붙여 나눈 나머지(체크섬)."""
    n = len(generator) - 1
    _, remainder, _ = mod2_div(data + "0" * n, generator)
    return remainder


def encode(data, generator):
    """송신 데이터 = 원래 데이터 + 체크섬."""
    return data + compute_checksum(data, generator)


def check(received, generator):
    """수신 측: 나머지가 0이면 True(오류 없음), 아니면 False(오류 검출)."""
    _, remainder, _ = mod2_div(received, generator)
    return "1" not in remainder


def print_division(data, generator):
    """교재 [그림 4-20] 형태로 나눗셈 과정을 출력한다."""
    n = len(generator) - 1
    dividend = data + "0" * n
    quotient, remainder, steps = mod2_div(dividend, generator, trace=True)
    pad = len(generator) + 1
    sp = lambda s: " ".join(s)

    print(" " * (2 * pad) + " " * (2 * n) + sp(quotient))
    print(sp(generator) + " | " + sp(dividend))
    for offset, current, divisor, result in steps:
        indent = " " * (2 * pad + 1 + 2 * offset)
        print(indent + sp(current))
        print(indent + sp(divisor) + "   (XOR)")
        print(indent + "-" * (2 * len(generator) - 1))
    print(" " * (2 * pad + 1 + 2 * (len(dividend) - n)) + sp(remainder) + "   <- 나머지(체크섬)")
    return remainder
