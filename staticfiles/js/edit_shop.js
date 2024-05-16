document.addEventListener('DOMContentLoaded',function(){const updateShopBtn=document.getElementById('updateShopBtn');updateShopBtn.addEventListener('click',function(event){event.preventDefault();const spinnerContainer=document.getElementById('updateShopBtn');spinnerContainer.innerHTML='';spinnerContainer.innerHTML=`
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Updating...
        `;const shopEditForm=document.getElementById('shopEditForm');const formData=new FormData(shopEditForm);const csrfToken=formData.get('csrfmiddlewaretoken');fetch('/vendors/edit-shop/',{method:'POST',body:formData,headers:{'X-CSRFToken':csrfToken}}).then(response=>response.json()).then(data=>{if(data.status==='success'){const modalBody=document.querySelector('.update-shop-modal');modalBody.innerHTML=`
                    <div class="alert alert-success" role="alert">
                        ${data.message}
                    </div>
                `;setTimeout(function(){window.location.reload()},1000)}else{const modalBody=document.querySelector('.update-shop-modal');modalBody.innerHTML=`
                    <div class="alert alert-success" role="alert">
                        Failed to update shop details.
                    </div>
                `;setTimeout(function(){window.location.reload()},1000)}}).catch(error=>{console.error('Error:',error);alert('An error occurred. Please try again.')})})})