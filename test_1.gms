func outer() {
    Num a;
    func inner() {
        a = 111;
        return a;
    }
    return inner();
}

print outer();


func loop(Num a) {
    print a;
    return 0 if a <= 0 else loop(a - 1);
}

print outer();
print loop(10);
