document.addEventListener("DOMContentLoaded",(function(){document.querySelectorAll('[id^="productDeleteConfirm"]').forEach((e=>{e.addEventListener("click",(function(n){n.preventDefault(),e.innerHTML='\n                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>\n                Deleting...\n            ';const t=e.dataset.itemid,o=function(e){let n=null;if(document.cookie&&""!==document.cookie){const t=document.cookie.split(";");for(let o=0;o<t.length;o++){const r=t[o].trim();if(r.startsWith(e+"=")){n=decodeURIComponent(r.substring(e.length+1));break}}}return n}("csrftoken");fetch(`/vendors/delete-item/${t}/`,{method:"POST",headers:{"X-CSRFToken":o,"Content-Type":"application/json"},body:JSON.stringify({item_id:t})}).then((e=>e.json())).then((n=>{const t=e.closest(".modal-content").querySelector(".delete-product-modal-body");"success"===n.status?t.innerHTML=`\n                        <div class="alert alert-success" role="alert">\n                            ${n.message}\n                        </div>\n                    `:t.innerHTML=`\n                        <div class="alert alert-danger" role="alert">\n                            ${n.message}\n                        </div>\n                    `,setTimeout((function(){window.location.reload()}),500)})).catch((n=>{console.error("Error:",n);e.closest(".modal-content").querySelector(".delete-product-modal-body").innerHTML='\n                    <div class="alert alert-danger" role="alert">\n                        An error occurred. Please try again.\n                    </div>\n                ',setTimeout((function(){window.location.reload()}),500)}))}))}))}));