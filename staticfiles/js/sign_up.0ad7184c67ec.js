document.addEventListener("DOMContentLoaded",(function(){const e=document.getElementById("registerBtn");e&&e.addEventListener("click",(function(n){n.preventDefault(),e.innerHTML='\n                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>\n                Signing Up...\n            ';const t={email:document.getElementById("emailInput").value,password:document.getElementById("passwordInput").value,phone_number:document.getElementById("phoneNumberInput").value,agree_to_terms:document.getElementById("agreeTermsInput").checked,is_vendor:!0},r=document.querySelector('input[name="csrfmiddlewaretoken"]').value;fetch("/accounts/vendor/sign-up/",{method:"POST",headers:{"Content-Type":"application/json","X-CSRFToken":r},body:JSON.stringify(t)}).then((e=>{if(!e.ok)throw new Error("Network response was not ok");return e.json()})).then((e=>{console.log(e);const n=document.querySelector(".vendor-registration-modal");e.success?(n.innerHTML=`\n                        <div class="alert alert-success" role="alert">\n                            <i class="bi bi-check-circle-fill"></i> ${e.success}\n                        </div>`,setTimeout((()=>{window.location.href="/accounts/dashboard/"}),3e3)):(n.innerHTML=`\n                        <div class="alert alert-danger" role="alert">\n                            <i class="bi bi-exclamation-triangle-fill"></i> ${e.error}\n                        </div>`,console.error("Sign up failed:",e.error),setTimeout((()=>{window.location.reload()}),4e3))})).catch((e=>{console.error("Error:",e)}))}))})),document.addEventListener("DOMContentLoaded",(function(){const e=document.getElementById("registerCustomerBtn");e&&e.addEventListener("click",(function(n){n.preventDefault(),e.innerHTML='\n                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>\n                Signing Up...\n            ';const t={email:document.getElementById("emailInput1").value,password:document.getElementById("passwordInput1").value,phone_number:document.getElementById("phoneNumberInput1").value,agree_to_terms:document.getElementById("agreeTermsInput1").checked,is_vendor:!1},r=document.querySelector('input[name="csrfmiddlewaretoken"]').value;fetch("/accounts/customer/sign-up/",{method:"POST",headers:{"Content-Type":"application/json","X-CSRFToken":r},body:JSON.stringify(t)}).then((e=>{if(!e.ok)throw new Error("Network response was not ok");return e.json()})).then((e=>{console.log(e);const n=document.querySelector(".customer_registration_modal");e.success?(n.innerHTML=`\n                        <div class="alert alert-success" role="alert">\n                            <i class="bi bi-check-circle-fill"></i> ${e.success}\n                        </div>`,setTimeout((()=>{window.location.href="/accounts/dashboard/"}),2e3)):(n.innerHTML=`\n                        <div class="alert alert-danger" role="alert">\n                            <i class="bi bi-exclamation-triangle-fill"></i> ${e.error}\n                        </div>`,console.error("Sign up failed:",e.error),setTimeout((()=>{window.location.reload()}),4e3))})).catch((e=>{console.error("Error:",e)}))}))})),window.onload=function(){initializeGA()};