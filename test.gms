{
    print 1;
    print 2;

    Num a, b, c;
    a = 1;
    b = 2;
    c = 3;
    {
        Num d;
        d = a + b;
        {
            Num e;
            e = (a * b + (c  / d + 1));
            print e;
        }
        print d;
    }
    print a + c;
}
