$(document).ready(function(){updateCartBadge();$('.add-to-cart-form').submit(function(e){e.preventDefault();var form=$(this);var itemID=form.find('input[name="item_id"]').val();var csrftoken=form.find('input[name="csrfmiddlewaretoken"]').val();var addToCartButton=form.find('button[type="submit"]');if(addToCartButton.text().trim()==="Add to Cart"){$.ajax({type:'POST',url:'/add_to_cart/',data:{'item_id':itemID,},headers:{'X-CSRFToken':csrftoken},success:function(response){if(response.message==="Item added to cart successfully."){addToCartButton.text("Remove from Cart");addToCartButton.removeClass("btn-outline-dark").addClass("btn-outline-danger");playNotificationSound();flashCartBadge();updateCartBadge();toggleCartSection()}},error:function(xhr,errmsg,err){console.log(xhr.status+": "+xhr.responseText)}})}});function updateCartBadge(){$.ajax({type:'GET',url:'/get_cart_items/',success:function(data){var numCartItems=data.num_items;$('.custom-cart-badge').text(numCartItems);toggleCartSection()},error:function(xhr,errmsg,err){console.log(xhr.status+": "+xhr.responseText)}})}
function playNotificationSound(){var audio=new Audio('/static/audio/add_to_cart_notification.mp3');audio.play()}
function flashCartBadge(){var badge=$('.custom-cart-badge');badge.addClass('text-bg-danger');setTimeout(function(){badge.removeClass('text-bg-danger')},1000)}
function toggleCartSection(){var numCartItems=parseInt($('.custom-cart-badge').text());var cartSection=$('.add-to-cart');if(numCartItems>0){cartSection.show()}else{cartSection.hide()}}});$(document).ready(function(){updateCartBadge();$('.add-to-cart-form').submit(function(e){e.preventDefault();var form=$(this);var itemID=form.find('input[name="item_id"]').val();var addToCartButton=form.find('button[type="submit"]');if(addToCartButton.text().trim()==="Remove from Cart"){$.ajax({type:'POST',url:'/remove_from_cart/'+itemID+'/',data:{'item_id':itemID,},headers:{'X-CSRFToken':getCsrfToken()},success:function(response){if(response.message==="Item removed from cart successfully."){addToCartButton.text("Add to Cart");addToCartButton.removeClass("btn-outline-danger").addClass("btn-outline-dark");updateCartBadge();toggleCartSection()}},error:function(xhr,errmsg,err){console.log(xhr.status+": "+xhr.responseText)}})}});function getCsrfToken(){return $('input[name="csrfmiddlewaretoken"]').val()}
function updateCartBadge(){$.ajax({type:'GET',url:'/get_cart_items/',success:function(data){var numCartItems=data.num_items;$('.custom-cart-badge').text(numCartItems);toggleCartSection()},error:function(xhr,errmsg,err){console.log(xhr.status+": "+xhr.responseText)}})}
function toggleCartSection(){var numCartItems=parseInt($('.custom-cart-badge').text());var cartSection=$('.add-to-cart');if(numCartItems>0){cartSection.show()}else{cartSection.hide()}}});document.addEventListener('DOMContentLoaded',function(){const registerBtn=document.getElementById('registerBtn');if(registerBtn){registerBtn.addEventListener('click',function(event){event.preventDefault();registerBtn.innerHTML=`
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
                        </div>`;console.error('Login failed:',data.error);setTimeout(()=>{window.location.reload()},2000)}}).catch(error=>{console.error('Error:',error);setTimeout(()=>{window.location.reload()},2000)})})}});function removeImgParams(){const imgElements=document.getElementsByTagName('img');for(let i=0;i<imgElements.length;i++){const imgElement=imgElements[i];let src=imgElement.getAttribute('src');if(src.includes('?')){src=src.split('?')[0];imgElement.setAttribute('src',src)}}}
window.onload=function(){removeImgParams()};$(document).ready(function(){const container=$('.search-results-container');function highlightMatch(text,query){const escapedQuery=query.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');const words=escapedQuery.split(/\s+/).filter(Boolean);const regexPattern=`\\b(${words.join('|')})\\b`;const regex=new RegExp(regexPattern,'gi');return text.replace(regex,'<span class="highlight-search">$&</span>')}
function updateSearchResults(query){if(query.length>0){$.ajax({url:'/search/',method:'GET',data:{query:query},success:function(response){const shopItems=response.shop_items;container.empty();if(shopItems.length>0){shopItems.forEach(item=>{const highlightedTitle=highlightMatch(item.title,query);const highlightedCategory=highlightMatch(item.category,query);const highlightedSubject=highlightMatch(item.subject,query);const highlightedEducationLevel=highlightMatch(item.education_level,query);const itemDetailUrl=`/${item.category_slug}/${item.id}/${item.slug}/`;const card=`
                                <div class="mb-3">
                                    <div class="card">
                                        <div class="card-body">
                                            <h5 class="card-title">
                                                <a href="${itemDetailUrl}" style="font-size: 18px; text-decoration: none; color: blue;">
                                                    ${highlightedTitle}
                                                </a>
                                            </h5>
                                            <div class="row">
                                                <div class="col">
                                                    <p class="card-text"><strong>Category</strong>: ${highlightedCategory}</p>
                                                </div>
                                                <div class="col">
                                                    <p class="card-text"><strong>Subject</strong>: ${highlightedSubject}</p>
                                                </div>
                                                <div class="col">
                                                    <p class="card-text"><strong>Level</strong>: ${highlightedEducationLevel}</p>
                                                </div>
                                                <div class="col">
                                                    <p class="card-text"><strong>Price</strong>: Ksh ${item.price}</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            `;container.append(card)});container.show()}else{container.html('<p>No results matched your query.</p>');container.show()}},error:function(xhr,status,error){console.error('Error fetching search results:',error)}})}else{container.hide()}}
$('#site-wide-search-form input[type="text"]').on('input',function(){const query=$(this).val().trim();updateSearchResults(query)});$(document).on('click',function(event){if(!$(event.target).closest('#site-wide-search-form').length&&!$(event.target).closest('.search-results-container').length){container.hide()}});$('#site-wide-search-form input[type="text"]').on('keyup',function(){const query=$(this).val().trim();if(query===''){container.hide()}});container.hide()});$(document).ready(function(){$('#subscribeButton').on('click',function(){const email=$('#newsletterEmail').val().trim();if(email){subscribeToNewsletter(email)}else{displaySubscriptionMessage({'error':'Please provide a valid email address.'})}})});function subscribeToNewsletter(email){const formData={'email':email};$.ajax({type:'POST',url:'/accounts/api/create-subscriber/',data:JSON.stringify(formData),contentType:'application/json',success:function(response){displaySubscriptionMessage(response)},error:function(xhr,status,error){console.error('Error subscribing to newsletter:',error);displaySubscriptionMessage({'error':'Failed to subscribe. Please try again later.'})}})}
function displaySubscriptionMessage(response){const messageContainer=$('#subscriptionMessageContainer');messageContainer.empty();if(response.message){messageContainer.addClass('text-success').text(response.message)}else if(response.error){messageContainer.addClass('text-danger').text(response.error)}};