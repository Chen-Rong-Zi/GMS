Num a;
a = 4321;
func ouuter() {
    a = 1111;
    func inner() {
        Num b;
        func inner1() {
            b = 3333;
            return b;

        }
        return inner1();
    }
    return inner();
}

print ouuter();
