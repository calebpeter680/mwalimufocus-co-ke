document.addEventListener("DOMContentLoaded",(function(){const e=document.getElementById("order-id");if(e){!function(e){const n=function(e){let n=null;if(document.cookie&&""!==document.cookie){const t=document.cookie.split(";");for(let o=0;o<t.length;o++){const c=t[o].trim();if(c.substring(0,e.length+1)===e+"="){n=decodeURIComponent(c.substring(e.length+1));break}}}return n}("csrftoken");$.ajax({type:"POST",url:`/send_attachment_via_email/${e}/`,dataType:"json",beforeSend:function(e){e.setRequestHeader("X-CSRFToken",n)},success:function(e){e.success},error:function(e,n,t){}})}(e.value)}}));