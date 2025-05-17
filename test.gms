Num own *p = new Num;
*p = 1234;
free(p);

Num own *q = p;
Num own *m = new Num;
*m = *q + 1234;

{
    Num own *abc = m;
    *abc = 1111;
    free(abc);
}

Num own *owner = new Num;
*owner = 111;
{
    Num shr *uniq_borrow = &shr *owner;
    Num shr *shr_borrow1 = &shr *owner;
    Num shr *shr_borrow2 = &shr *owner;
    Num shr *shr_borrow3 = &shr *owner;
    Num shr *shr_borrow4 = &shr *owner;
    Num shr *shr_borrow5 = &shr *shr_borrow4;

    print shr_borrow1;
    print shr_borrow2;
    print shr_borrow3;
    print shr_borrow4;
    print shr_borrow5;
    print uniq_borrow;
}
print *owner;
