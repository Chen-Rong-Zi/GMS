func add1(Num a) { Num b;}
print add1(2);

func big(Num a) {
    {
        return 1;
    }
    return 2;
}
print big(1);

func fact(Num a) {
    return (1) if (a <= 1) else (a * fact(a - 1));
}

func fib(Num n) {
    return 1 if n <= 1 else (fib(n - 1) + fib(n - 2));
}

Num a;
a = 4321;
func ouuter() {
    return a;
}

func test_free_variable() {
    Num a;
    a = 1234;
    return ouuter();
}

print fact(10);
print (ouuter());
print (test_free_variable());
