var image_tracker='g';
function change(){
  var image = document.getElementById('image');
  if(image_tracker=='g'){
     image.src = "http://127.0.0.1:8000/static/factory.jpg";
     image_tracker='b';
   }
  else{
    image.src = "http://127.0.0.1:8000/static/brick.jpg";
    image_tracker = 'g';
   }
}