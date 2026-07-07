class Calculator:
    def add(self, a: int, b: int) -> int:
        return a + b

    def divide(self, a: int, b: int) -> float:
        if b == 0:
            raise ValueError("division by zero")
        return a / b

    def complex_calc(self, x: float) -> float:
        result = 0.0
        for i in range(10):
            if i % 2 == 0:
                result += x * i
            else:
                result -= x * i
        return result


class AdvancedCalculator(Calculator):
    def power(self, base: float, exp: int) -> float:
        result = 1.0
        for _ in range(exp):
            result *= base
        return result
