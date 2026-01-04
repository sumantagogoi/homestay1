function checksum(g){
  let a=48,b=55,c=36,d=58;
  var sum=0;
  var cc;
  var i;
  for(i=0;i<14;i++){
    cc=parseInt(g.charCodeAt(i));
    var w=cc<d?cc-a:cc-b;
    var pos=(i%2)+1;
    w=w*pos;
    var rem=w%c;
    var qo=parseInt(w/c);
    sum+=rem+qo;
  }
  sum=c-(sum%c);
  sum=sum==36?0:sum;
  cc=sum<10?sum+a:sum+55;
  checks=parseInt(g.charCodeAt(14));
  return checks==cc?true:false;
}
