document.querySelector('button').addEventListener('click', () => {
    const newForm = document.createElement('input');
    newForm.type = 'text';
  
    const newLabel = document.createElement('label');
    newLabel.textContent = '連絡事項：';
  
    newLabel.appendChild(newForm);
    document.querySelector('div').appendChild(newLabel);

    

    const output = document.querySelector('#output');


    //マウス移動時
    document.onmousemove = function(e) {
        output.innerHTML = `x:` + e.pageX + ` y:` + e.pageY;
    }


    //マウス離脱時
    document.onmouseout = function(e) {
        output.innerHTML = ``;
    }

});