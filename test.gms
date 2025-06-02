Num own *p = new Num;
*p = 1234;

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
    print shr_borrow1;
    print uniq_borrow;
}
print *owner;
