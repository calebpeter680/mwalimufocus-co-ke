document.addEventListener("DOMContentLoaded",(function(){const e=document.getElementById("loginBtn");e&&e.addEventListener("click",(function(n){n.preventDefault(),e.innerHTML='\n                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>\n                Logging In...\n            ';const o={email:document.getElementById("InputEmail2").value,password:document.getElementById("InputPassword2").value},t=document.querySelector('input[name="csrfmiddlewaretoken"]').value;fetch("/accounts/login/",{method:"POST",headers:{"Content-Type":"application/json","X-CSRFToken":t},body:JSON.stringify(o)}).then((e=>{if(!e.ok)throw new Error("Network response was not ok");return e.json()})).then((e=>{console.log(e);const n=document.querySelector(".login-modal");e.success?(n.innerHTML=`\n                        <div class="alert alert-success" role="alert">\n                            <i class="bi bi-check-circle-fill"></i> ${e.success}\n                        </div>`,setTimeout((()=>{window.location.href="/accounts/dashboard/"}),2e3)):(n.innerHTML=`\n                        <div class="alert alert-danger" role="alert">\n                            <i class="bi bi-exclamation-triangle-fill"></i> ${e.error}\n                        </div>`,console.error("Login failed:",e.error),setTimeout((()=>{window.location.reload()}),2e3))})).catch((e=>{console.error("Error:",e),setTimeout((()=>{window.location.reload()}),2e3)}))}))}));