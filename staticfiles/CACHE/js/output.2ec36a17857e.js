document.addEventListener('DOMContentLoaded',function(){const registerBtn=document.getElementById('registerBtn');if(registerBtn){registerBtn.addEventListener('click',function(event){event.preventDefault();registerBtn.innerHTML=`
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Signing Up...
            `;const email=document.getElementById('emailInput').value;const password=document.getElementById('passwordInput').value;const phone_number=document.getElementById('phoneNumberInput').value;const agree_to_terms=document.getElementById('agreeTermsInput').checked;const formData={email:email,password:password,phone_number:phone_number,agree_to_terms:agree_to_terms,is_vendor:!0};const csrfToken=document.querySelector('input[name="csrfmiddlewaretoken"]').value;fetch('/accounts/vendor/sign-up/',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrfToken},body:JSON.stringify(formData)}).then(response=>{if(!response.ok){throw new Error('Network response was not ok')}
return response.json()}).then(data=>{console.log(data);const modalBody=document.querySelector('.vendor-registration-modal');if(data.success){modalBody.innerHTML=`
                        <div class="alert alert-success" role="alert">
                            <i class="bi bi-check-circle-fill"></i> ${data.success}
                        </div>`;setTimeout(()=>{window.location.href='/accounts/dashboard/'},3000)}else{modalBody.innerHTML=`
                        <div class="alert alert-danger" role="alert">
                            <i class="bi bi-exclamation-triangle-fill"></i> ${data.error}
                        </div>`;console.error('Sign up failed:',data.error);setTimeout(()=>{window.location.reload()},4000)}}).catch(error=>{console.error('Error:',error)})})}});document.addEventListener('DOMContentLoaded',function(){const registerBtn=document.getElementById('registerCustomerBtn');if(registerBtn){registerBtn.addEventListener('click',function(event){event.preventDefault();registerBtn.innerHTML=`
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Signing Up...
            `;const email=document.getElementById('emailInput1').value;const password=document.getElementById('passwordInput1').value;const phone_number=document.getElementById('phoneNumberInput1').value;const agree_to_terms=document.getElementById('agreeTermsInput1').checked;const formData={email:email,password:password,phone_number:phone_number,agree_to_terms:agree_to_terms,is_vendor:!1,};const csrfToken=document.querySelector('input[name="csrfmiddlewaretoken"]').value;fetch('/accounts/customer/sign-up/',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrfToken},body:JSON.stringify(formData)}).then(response=>{if(!response.ok){throw new Error('Network response was not ok')}
return response.json()}).then(data=>{console.log(data);const modalBody=document.querySelector('.customer_registration_modal');if(data.success){modalBody.innerHTML=`
                        <div class="alert alert-success" role="alert">
                            <i class="bi bi-check-circle-fill"></i> ${data.success}
                        </div>`;setTimeout(()=>{window.location.href='/accounts/dashboard/'},2000)}else{modalBody.innerHTML=`
                        <div class="alert alert-danger" role="alert">
                            <i class="bi bi-exclamation-triangle-fill"></i> ${data.error}
                        </div>`;console.error('Sign up failed:',data.error);setTimeout(()=>{window.location.reload()},4000)}}).catch(error=>{console.error('Error:',error)})})}});document.addEventListener('DOMContentLoaded',function(){const loginBtn=document.getElementById('loginBtn');if(loginBtn){loginBtn.addEventListener('click',function(event){event.preventDefault();loginBtn.innerHTML=`
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Logging In...
            `;const email=document.getElementById('InputEmail2').value;const password=document.getElementById('InputPassword2').value;const formData={email:email,password:password};const csrfToken=document.querySelector('input[name="csrfmiddlewaretoken"]').value;fetch('/accounts/login/',{method:'POST',headers:{'Content-Type':'application/json','X-CSRFToken':csrfToken},body:JSON.stringify(formData)}).then(response=>{if(!response.ok){throw new Error('Network response was not ok')}
return response.json()}).then(data=>{console.log(data);const modalBody=document.querySelector('.login-modal');if(data.success){modalBody.innerHTML=`
                        <div class="alert alert-success" role="alert">
                            <i class="bi bi-check-circle-fill"></i> ${data.success}
                        </div>`;setTimeout(()=>{window.location.href='/accounts/dashboard/'},2000)}else{modalBody.innerHTML=`
                        <div class="alert alert-danger" role="alert">
                            <i class="bi bi-exclamation-triangle-fill"></i> ${data.error}
                        </div>`;console.error('Login failed:',data.error);setTimeout(()=>{window.location.reload()},2000)}}).catch(error=>{console.error('Error:',error);setTimeout(()=>{window.location.reload()},2000)})})}});