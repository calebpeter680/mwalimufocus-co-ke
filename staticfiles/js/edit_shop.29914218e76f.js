document.addEventListener("DOMContentLoaded",(function(){document.getElementById("updateShopBtn").addEventListener("click",(function(e){e.preventDefault();const n=document.getElementById("updateShopBtn");n.innerHTML="",n.innerHTML='\n            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>\n            Updating...\n        ';const t=document.getElementById("shopEditForm"),o=new FormData(t),r=o.get("csrfmiddlewaretoken");fetch("/vendors/edit-shop/",{method:"POST",body:o,headers:{"X-CSRFToken":r}}).then((e=>e.json())).then((e=>{if("success"===e.status){document.querySelector(".update-shop-modal").innerHTML=`\n                    <div class="alert alert-success" role="alert">\n                        ${e.message}\n                    </div>\n                `,setTimeout((function(){window.location.reload()}),1e3)}else{document.querySelector(".update-shop-modal").innerHTML='\n                    <div class="alert alert-success" role="alert">\n                        Failed to update shop details.\n                    </div>\n                ',setTimeout((function(){window.location.reload()}),1e3)}})).catch((e=>{console.error("Error:",e),alert("An error occurred. Please try again.")}))}))}));