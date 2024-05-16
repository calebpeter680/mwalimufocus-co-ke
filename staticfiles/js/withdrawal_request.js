$(document).ready(function(){var sendRequestBtn=$('#sendRequestBtn');var debounceTimeout=60000;var localStorageKey='withdrawalRequestTime';sendRequestBtn.click(function(event){event.preventDefault();sendRequestBtn.html(`
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Sending...
        `);var lastRequestTime=localStorage.getItem(localStorageKey);if(lastRequestTime){var currentTime=new Date().getTime();var timeElapsed=currentTime-parseInt(lastRequestTime,10);if(timeElapsed<debounceTimeout){$('.withdrawal-request-modal-body').html(`
                    <div class="alert alert-dark" role="alert">
                        You must wait for at least 10 minutes before attempting another withdrawal request.
                    </div>
                `);sendRequestBtn.html('Send Request');setTimeout(function(){location.reload()},4000);return}}
var csrfToken=$('#requestWithdrawalForm input[name="csrfmiddlewaretoken"]').val();var formData=$('#requestWithdrawalForm').serialize();$.ajax({type:'POST',url:'/vendors/initiate_mpesa_b2c/',data:formData,headers:{'X-CSRFToken':csrfToken},success:function(response){$('.withdrawal-request-modal-body').html(`
                    <div class="alert alert-dark" role="alert">
                        ${response.status}
                    </div>
                `);localStorage.setItem(localStorageKey,new Date().getTime().toString());sendRequestBtn.html('Send Request');setTimeout(function(){location.reload()},4000)},error:function(xhr,status,error){console.error('Error:',error);$('.withdrawal-request-modal-body').html(`
                    <div class="alert alert-dark" role="alert">
                        An Error Occurred. Try Again
                    </div>
                `);sendRequestBtn.html('Send Request');setTimeout(function(){location.reload()},4000)}})})})