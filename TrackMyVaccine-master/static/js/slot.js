var container = document.getElementById('container')


$("#n").bind('keyup mouseup', function () {
    var n = document.getElementById('n').valueAsNumber
    container.innerHTML = '';
    for (var i =0; i < n; i++){
        container.insertAdjacentHTML('beforeend',
         `<div class="form-row">
            <div class="form-group col-sm-4">
              <label for="start"><strong>From</strong></label>
              <input type="time" class="form-control" id="start" name="start${i}">
            </div>
            <div class="form-group col-sm-4">
              <label for="to"><strong>To</strong></label>
              <input type="time" class="form-control" id="to" name="to${i}">
            </div>
            <div class="form-group col-sm-4">
              <label for="count"><strong>Count</strong></label>
              <input type="number" step = "1" min="1" class="form-control" id="count" name="count${i}">
            </div>
        </div>`);
    } 
});