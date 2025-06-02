Num own *p = new Num;
*p = 1234;
print p;
Num uniq *unia0 = & uniq *p;
*unia0 = 3333;
print unia0;

print p;
free(p);

{
    {
        print 1  + 2 + 34;
    }
}
