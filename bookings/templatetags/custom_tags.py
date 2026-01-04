from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    if value and arg:
        return '{:.2f}'.format(round((float(value) * float(arg)),1))
    else:
        return ""

@register.simple_tag
def totalAmt(amt, qant, rate, mrpdisc):
    if amt and qant and str(rate):
        return '{:.2f}'.format(round((float(amt) * float(qant) * (1+float(0)/100))- (mrpdisc/(1+float(rate)/100)) ,1 ))
    else:
        return ""

@register.filter
def normalize(num):
  if num % 1 == 0:
    return int(num)
  else:
    return num


@register.simple_tag
def price_per_unit_afterdiscount(price,disc,quant,gstr):
    return '{:.2f}'.format(float(price)-(float(disc)/(1+float(gstr)/100))/float(quant))
