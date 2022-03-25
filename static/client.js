
// handle stripe payment
var stripe = Stripe('pk_test_51KdQeLEtCEqhAcFnDKC9pUnPBfzcw58HF325ikZxcQtkAjX7IuFeehuaIzLnn9W1ZAWWSYezx99jXI9m64QDcrV200RcPqyuTw');
var elements = stripe.elements();
// Custom styling can be passed to options when creating an Element.
var style = {
  base: {
    // Add your base input styles here. For example:
    fontSize: '16px',
    color: '#32325d',
  },
};

// Create an instance of the card Element.
var card = elements.create('card', {style: style});

// Add an instance of the card Element into the `card-element` <div>.
card.mount('#card-element');
// Create a token or display an error when the form is submitted.
var form = document.getElementById('payment-form');
form.addEventListener('submit', function(event) {
  event.preventDefault();

  stripe.createToken(card).then(function(result) {
    if (result.error) {
      // Inform the customer that there was an error.
      var errorElement = document.getElementById('card-errors');
      errorElement.textContent = result.error.message;
    } else {
      // Send the token to your server.
      stripeTokenHandler(result.token);
    }
  });
});
function stripeTokenHandler(token) {
  // Insert the token ID into the form so it gets submitted to the server
  var form = document.getElementById('payment-form');
  var hiddenInput = document.createElement('input');
  hiddenInput.setAttribute('type', 'hidden');
  hiddenInput.setAttribute('name', 'stripeToken');
  hiddenInput.setAttribute('value', token.id);
  form.appendChild(hiddenInput);

  // Submit the form
  form.submit();
}

//------------------------------------------------------------------------------
let rows = document.querySelectorAll("table > tbody > tr");
rows.forEach(function(row){
  row.addEventListener('click', rowClick)
})

function rowClick(event){
  event.preventDefault(); 
  var data = event.target.parentElement; 
  game_id = data.childNodes[1].outerText; 
  team_name = data.childNodes[5].outerText; 
  point_spread = data.childNodes[7].outerText; 
  var id = document.getElementById('game_id');
  var name = document.getElementById('team_name'); 
  var spread = document.getElementById('point_spread'); 

  id.value = game_id; 
  name.value = team_name; 
  spread.value = point_spread;  
}
/*
rows.addEventListener('click', function(event){
  event.preventDefault(); 
  print("ROW CLICKED");
  var data = event.currentTarget.document.querySelectorAll(".row-data")
  game_id = data[0].innerHTML;
  team_name = data[2].innerHTML;
  point_spread = data[3].innerHTML;

  var id = document.getElementById('game_id');
  var name = document.getElementById('team_name'); 
  var spread = document.getElementById('point_spread'); 

  id.value = game_id; 
  name.value = team_name; 
  spread.value = point_spread; 

}); 
*/