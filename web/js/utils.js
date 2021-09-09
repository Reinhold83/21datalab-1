function http_get(myUrl) {
  var xmlHttp = new XMLHttpRequest();
  xmlHttp.open("GET", myUrl, false); // syncronous request
  xmlHttp.send(null);
  return xmlHttp.responseText;
}

// Create new function for file download

function http_file_post(url, data, params, obj, cb) {
  // construct an HTTP request
  var xhr = new XMLHttpRequest();
  xhr.open("POST", url, true); //asynchronous call
  xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
  xhr.responseType = 'blob';
  xhr.onload = function (e) {
    var blob = e.currentTarget.response;
    var contentDispo = e.currentTarget.getResponseHeader('Content-Disposition');
    // https://stackoverflow.com/a/23054920/
    var fileName = contentDispo.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)[1];
    saveOrOpenBlob(blob, fileName);
  }
  xhr.send(data);
}


function saveOrOpenBlob(blob, fileName) {
  var a = document.createElement('a');
  a.href = window.URL.createObjectURL(blob);
  a.download = fileName;
  a.dispatchEvent(new MouseEvent('click'));
}


function http_post(url, data, params, obj, cb) {
  // construct an HTTP request
  var xhr = new XMLHttpRequest();
  xhr.open("POST", url, true); //asynchronous call
  xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
  xhr.onreadystatechange = function () {
    if (xhr.readyState == XMLHttpRequest.DONE) {
      if (xhr.status > 201) {
        console.log("error calling ", url, xhr.status, xhr.responseText);
      }
      if (cb != null) {
        cb(obj, xhr.status, xhr.responseText, params);
      }
    }
  }
  // send the collected data as JSON
  xhr.send(data);
}

function http_post_sync(url, jsonStringify, data) {
  let xhr = new XMLHttpRequest()
  let inputData
  if (jsonStringify === true) {
    inputData = JSON.stringify(data)
  } else {
    inputData = data
  }
  xhr.open("POST", url, false)
  xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8')
  xhr.send(inputData)
  return xhr
}

function http_delete(url, data, params, obj, cb) {
  // construct an HTTP DELETE request
  var xhr = new XMLHttpRequest();
  xhr.open("DELETE", url, true); //asynchronous call
  xhr.setRequestHeader('Content-Type', 'application/json; charset=UTF-8');
  xhr.onreadystatechange = function () {
    if (xhr.readyState == XMLHttpRequest.DONE) {
      if (xhr.readyState == XMLHttpRequest.DONE) {
        if (xhr.status > 201) {
          console.log("error calling ", url, xhr.status);
        }
        if (cb != null) {
          cb(obj, xhr.status, xhr.responseText, params);
        }
      }
    }
  }
  xhr.send(data);
}