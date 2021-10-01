/* move this to cockpit widget later */
_helper_log('cockpit importer load')
var cockpiteventSource = 0
var cockpitPath = ""
var cockpitWidgetPath = ""
var importerFields
var importerStepNo = 1
var importerFileName
var importerFileNameList = []
var importerHeaderExists = undefined
var activePanelIndex = -1

// --- FOR TESTING PURPOSES
// --- [TODO] remove
function cockpit_importer_test() {
  _helper_log('cockpit_importer_test')
  // _helper_modal_activate_step_no(4)
  http_post("/_execute", cockpitPath + ".importer_import", null, null, (self, status, data, params) => { })
}

// --- initializes the cockpit
function cockpit_init(path) {
  // --- [TODO] remove
  _helper_log('cockpit_importer_init')
  cockpitPath = path
  console.log('cockpitPath', cockpitPath)
  $("#cockpit").attr("path", path)
  cockpiteventSource = new EventSource('/event/stream');
  cockpiteventSource.addEventListener(`${cockpitPath.substr(5)}.importer_preview.data_imported`, (e) => {
    console.log('e', e)
    cockpit_importer_2_approve_file_finished()
  });
  cockpit_importer_1_choose_file()
}

// --- Choose File (STEP 1)
function cockpit_importer_1_choose_file() {
  importerFileNameList = [];
  // --- [TODO] remove
  _helper_log('cockpit_importer_1_choose_file')
  _helper_modal_activate_step_no(1)
  const files = JSON.parse(http_get('/_upload'));
  const filesLength = files.length;
  const selector = '#importer-content-1'
  $(selector).html('Waiting for file list to load!')
  let filesHtml = '<b>No files available!</b>';
  if (filesLength > 0) {
    filesHtml = `<thead><tr style="text-align: left;"><th style="text-align: center;">Select</th><th>File</th><th>Size</th><th>Date Created</th></tr></thead><tbody style="text-align: left;">`;
    for (var fileNo = 0, length = filesLength; fileNo < length; fileNo++) {
      const file = files[fileNo];
      filesHtml = `${filesHtml}<tr>`;
      filesHtml += `<td style="text-align: center;"><input type="checkbox" class="" id="importer-choose-file-select-${file.name}" filename="${file.name}" onchange="cockpit_importer_1_select_file(this)"></td>`;
      filesHtml += `<td>${file.name}</td>`;
      filesHtml += `<td>${file.size} MB</td>`;
      filesHtml += `<td>${file.time} </td>`;
      // filesHtml += `<td><button type="button" class="btn btn-info" onclick="cockpit_importer_2_approve_file('${file.name}')">Next (Import File) ></button></td>`;
      filesHtml += `</tr>`;
    }
    filesHtml = `<div style="max-height:400px; overflow:auto;"><table class="table table-dark table-striped">${filesHtml}</tbody></table></div>`;
  }
  $(selector).html(filesHtml);

  $('#importer-cockpit-next').html(`<button type="button" class="btn btn-primary" style="margin-top:1rem" onclick="cockpit_importer_2_approve_file()">Next</button>`);
}

function cockpit_importer_1_select_file(filename) {
  importerFileNameList = [];
  $("input[id^=importer-choose-file-select-]").each(function (index, el) {
    if (el.checked == true){
      importerFileNameList.push(el.getAttribute('filename'))
    }else{
      const index = importerFileNameList.indexOf(el.getAttribute('filename'));
      if (index > -1) {
        importerFileNameList.splice(index, 1);
      }
    };
  });
}

// --- Approve File (STEP 2)
function cockpit_importer_2_approve_file(filename) {
  // --- [TODO] remove
  _helper_log('cockpit_importer_2_approve_file')
  // --- set global filename
  if (importerFileNameList.length == 0)
    return;
  _helper_modal_activate_step_no(2)
  const selector = '#importer-content-2'
  $(selector).html('Waiting for file preview to load!')
  // --- set filename
  let path = $("#cockpit").attr("path");
  let query = [];
  for (let x of importerFileNameList){
    query.push({ browsePath: path + ".importer_preview.fileName",
    value: x })
  }
  // let query = importerFileNameList.map({ browsePath: path + ".importer_preview.fileName", value: importerFileName })
  http_post("/setProperties", JSON.stringify(query), null, null, function (obj, status, data, params) {

    // --- delete current data_preview
    query = [{ browsePath: path + ".importer_preview.data_preview", value: undefined }];
    http_post("/setProperties", JSON.stringify(query), null, null, function (obj, status, data, params) {

      // --- run import function
      http_post("/_execute", cockpitPath + ".importer_preview", null, null, (self, status, data, params) => {
        let importerApproveHtml = ``
        if (status !== 200) {
          importerApproveHtml = `<p>Something went wrong while loading the file!</p>`
          $(selector).html(importerApproveHtml)
        } else {
          importerApproveHtml = `<p>Waiting for file to load!</p>`
          $(selector).html(importerApproveHtml)
        }
      })
    })
  })
}

function cockpit_importer_2_approve_file_finished() {
  _helper_log(`im.importer_preview.data_imported`)
  const selector = '#importer-content-2'
  // --- get data from node
  http_post("_getbranchpretty", cockpitPath + ".importer_preview.data_preview", null, null, function (obj, status, data, params) {
    const node = JSON.parse(data)
    const value = JSON.parse(node[".properties"].value)
    importerFields = value.schema.fields
    const dat = value.data
    let fieldsHtml = `<thead style="text-align: center;">`
    // --- loop through fields
    for (var fieldNo = 1, len = importerFields.length; fieldNo < len; fieldNo++) {
      const field = importerFields[fieldNo]
      fieldsHtml = `${fieldsHtml}<th>${field.name}</th>`
    }
    fieldsHtml = `<tr>${fieldsHtml}</tr></thead><tbody style="text-align: center;">`
    // --- loop through data
    let datHtml = ``
    for (var datNo = 0, datLen = dat.length; datNo < datLen; datNo++) {
      const row = dat[datNo]
      datHtml = `${datHtml}<tr>`
      // --- loop through fields
      for (var fieldNoDat = 1, fieldLen = importerFields.length; fieldNoDat < fieldLen; fieldNoDat++) {
        const field = importerFields[fieldNoDat]
        datHtml = `${datHtml}<td>${row[field.name]}</td>`
      }
      datHtml = `${datHtml}</tr>`
    }
    const actionBtnHtml = `
      <div class="text-center"> 
        <button type="button" class="btn btn-info" onclick="_helper_modal_activate_step_no(1)">< (1) Choose File</button>
        <button type="button" class="btn btn-info" onclick="cockpit_importer_3a_define_header_file_contains_header()">(3) Define Header (File contains header) ></button>
        <button type="button" class="btn btn-info" onclick="cockpit_importer_3b_define_header_file_misses_header()">(3) Define Header (File misses header) ></button>
      </div>
    `

    importerApproveHtml = `
      <div class="table-responsive" style="max-height:400px">
        <table class="table table-dark table-striped" style="margin-bottom:0px">${fieldsHtml}${datHtml}</tbody></table>
      </div>
    `
    $(selector).html(importerApproveHtml);
    $('#importer-cockpit-next').html(`<button type="button" class="btn btn-primary" onclick="cockpit_importer_3a_define_header_file_contains_header()" style="margin-top:1rem;">Next</button>`);
  })
}

// --- Define Header: file contains header (STEP 3a)
function cockpit_importer_3a_define_header_file_contains_header() {
  importerHeaderExists = true
  _helper_log('cockpit_importer_3a_define_header_file_contains_header')
  _helper_modal_activate_step_no(3)
  const selector = '#importer-content-3'
  $(selector).html('Waiting for header fields to load!')
  let html = ``
  for (var fieldNo = 2, fieldsLen = importerFields.length; fieldNo < fieldsLen; fieldNo++) {
    const field = importerFields[fieldNo]
    html = `${html}
      <tr style="text-align: center;">
        <td>${field.name}</td>
        <td>
          <div class="form-check">
            <input type="checkbox" class="" fieldvalue="${field.name}" checked id="importer-field-name-${fieldNo}">
          </div>
        </td>
      </tr>
    `
  }
  const actionBtnHtml = `
    <div class="text-center"> 
      <button type="button" class="btn btn-info" onclick="_helper_modal_activate_step_no(2)">< (2) Approve File</button>
      <button type="button" class="btn btn-info" onclick="cockpit_importer_4_define_table()">(4) Define Table ></button>
    </div>
  `
  html = `
    <div class="table-responsive" style="max-height:400px">
      <table class="table table-dark table-striped">
        <thead>
          <tr style="text-align: center;">
            <th>Name</th>
            <th>
              <input type="checkbox" class="" checked id="importer-field-nameall" onchange="cockpit_importer_3_field_import_select_all()">
              &nbsp;&nbsp;Import all
            </th>
          </tr>
        </thead>
        <tbody>
          ${html}
        </tbody>
      </table>
    </div>
  `
  $(selector).html(html);
  $('#importer-cockpit-next').html(`<button type="button" class="btn btn-primary" onclick="cockpit_importer_5_finish_import()" style="margin-top:1rem;">Next</button>`);
  // $('#importer-content-3').html(defineHeaderHtml)
}

function cockpit_importer_3_field_import_select_all() {
  _helper_log('cockpit_importer_3_field_import_select_all')
  var check_all = $("input[id^=importer-field-nameall]").prop('checked');
  $("input[id^=importer-field-name-]").each(function (index, el) {
    $(el).prop('checked', check_all);
  })
}

// --- Define Header: file misses header (STEP 3b)
function cockpit_importer_3b_define_header_file_misses_header() {
  importerHeaderExists = false
  _helper_log('cockpit_importer_3b_define_header_file_misses_header')
  _helper_modal_activate_step_no(3)
  const selector = '#importer-content-3'
  $(selector).html('Waiting for header fields to load!')
  let html = ``
  for (var fieldNo = 1, fieldsLen = importerFields.length; fieldNo < fieldsLen; fieldNo++) {
    const field = importerFields[fieldNo]
    html = `${html}
      <tr style="text-align: center">
        <td style="padding-top: 20px">${field.name}</td>
        <td>
          <div class="form-group">
            <input type="text" class="form-control" placeholder="Enter field name" id="importer-field-name-${fieldNo}">
          </div>
        </td>
        <td>
          <div class="form-check">
            <input type="checkbox" style="width: 30px; height: 30px" class="" id="importer-field-name-${fieldNo}">
          </div>
        </td>
        <td>
          <div class="form-check">
            <input type="checkbox" style="width: 30px; height: 30px" onclick="_helper_checkbox_time(${fieldNo})" class="" id="importer-field-time-${fieldNo}">
          </div>
        </td>
      </tr>
    `
  }
  const actionBtnHtml = `
    <div class="text-center"> 
      <button type="button" class="btn btn-info" onclick="_helper_modal_activate_step_no(2)">< (2) Approve File</button>
      <button type="button" class="btn btn-info" onclick="cockpit_importer_4_define_table()">(4) Define Table ></button>
    </div>
    `
  html = `
    ${actionBtnHtml}
    <div class="table-responsive">
      <table class="table table-dark table-striped">
        <thead>
          <tr style="text-align: center;">
            <th>Example value</th>
            <th>Field name</th>
            <th>Import</th>
            <th>Time value</th>
          </tr>
        </thead>
        <tbody>
          ${html}
        </tbody>
      </table>
    </div>
    ${actionBtnHtml}
  `
  $(selector).html(html)
}

// --- Define Table (STEP 4)
function cockpit_importer_4_define_table() {
  _helper_log('cockpit_importer_4_define_table')
  _helper_modal_activate_step_no(4)
  const filename = importerFileName
  const tablename = filename.replace('.', '_')
  const tablepath = 'imports/' + tablename
  const selector = '#importer-content-4'
  const actionBtnHtml = `
    <div class="text-center"> 
      <button type="button" class="btn btn-info" onclick="_helper_modal_activate_step_no(3)">< (3) Define Header</button>
      <button type="button" class="btn btn-info" onclick="cockpit_importer_5_finish_import()"> (5) Finish Import ></button>
    </div>
  `
  const html = `
    ${actionBtnHtml}
    <div class="form-group">
      <label for="tablename">Tablename:</label>
      <input type="text" class="form-control" placeholder="Enter tablename. Default (${tablename})" id="importer-tablename">
    </div>
    <div class="form-group">
      <label for="tablepath">Tablepath:</label>
      <input type="text" class="form-control" placeholder="Enter tablepath (for exmple: tables/mytable). Default (${tablepath})" id="importer-tablepath">
    </div>
    ${actionBtnHtml}
  `
  $(selector).html(html)
}

// --- Finish Import (STEP 5)
function cockpit_importer_5_finish_import() {
  let msg
  let btnHtml = `
    <div class="text-center"> 
      <button type="button" class="btn btn-info" onclick="_helper_modal_activate_step_no(1)">< (1) Choose File</button>
      <button type="button" class="btn btn-info" onclick="_helper_modal_activate_step_no(2)">< (2) Approve File</button>
      <button type="checked" class="btn btn-info" onclick="_helper_modal_activate_step_no(3)">< (3) Define Table</button>
      <button type="button" class="btn btn-info" onclick="_helper_modal_activate_step_no(4)">< (4) Define Header</button>
    </div>
  `
  btnHtml = ``
  // --- [TODO] remove
  _helper_log('cockpit_importer_5_finish_import')
  // --- activate modals tab-pane
  _helper_modal_activate_step_no(4)
  // --- set jquery selector
  const selector = '#importer-content-4'
  // --- define importer object
  const fields = []
  let timefield = undefined

  if ($("input[id^=importer-field-nameall]").prop('checked')){
    fields.push("*")
  }else{
    $("input[id^=importer-field-name-]").each(function (index, el) {
      const id = $(el).attr('id')
      const no = id.substr(id.lastIndexOf('-') + 1)
      // const val = $(el).val() === "" ? no : $(el).val()
      const val = $('#importer-field-name-' + no).attr('fieldvalue')
      const use = $('#importer-field-name-' + no).is(":checked")

      if (use === true) {
        fields.push(val)
      }
      timefield = no
    })
  }

  let tablename = $("#importer-tablename").val()
  let tablepath = $("#importer-tablepath").val()
  const filename = importerFileNameList.join("_")

  if (tablename === '') {
    tablename = filename.replace('.', '_')
  }
  tablepath = 'root.imports.' + tablename
  /*if (tablepath === '') {
    tablepath = 'root.imports.' + tablename
  } else {
    tablepath = 'root.' + $("#importer-tablepath").val().replace('/', '.') + tablename
  } */
  const importerObj = { variables:fields, filenames: importerFileNameList}
  // --- update html
  msg = 'Waiting for import to be finished!'
  $(selector).html(_helper_html_wrap(msg, btnHtml))
  // --- create response var
  let res

  /*
  // // --- [api] create table node
  // res = http_post_sync('/_create', true, [ { browsePath: tablepath, type: 'table' } ])
  // msg = `Failed creating table '${tablepath}'!`
  // if ( res.status > 201 ) $(selector).html(_helper_html_wrap(msg, btnHtml))

  // --- [api] set importer.tablename
  res = http_post_sync('/_create', true, [{ browsePath: `${cockpitPath}.importer_import.tablename`, type: 'const' }])
  msg = `Failed creating const 'root.importer.tablename'!`
  if (res.status > 201) $(selector).html(_helper_html_wrap(msg, btnHtml))

  // --- [api] set const root.importer.filename
  if (res.status <= 201)
    res = http_post_sync('/setProperties', true, [{ browsePath: `${cockpitPath}.importer_import.tablename`, value: tablename }])
  msg = `Failed setting value for const 'root.importer.tablename'!`
  if (res.status > 201) $(selector).html(_helper_html_wrap(msg, btnHtml))

  // --- [api] create referencer columns
  // if (res.status <= 201)
  //   res = http_post_sync('/_create', true, [{ browsePath: `${cockpitPath}.importer_import.metadata`, type: 'const' }])
  // msg = `Failed creating const '${tablepath + ".metadata"}'!`
  // if (res.status > 201) $(selector).html(_helper_html_wrap(msg, btnHtml))

  // --- [api] set fields
  if (res.status <= 201)
  */
  res = http_post_sync('/setProperties', true, [{ browsePath: `${cockpitPath}.importer_import.metadata`, value: JSON.stringify(importerObj) }])
  msg = `Failed setting value for const '${tablepath + ".metadata"}'!`
  if (res.status > 201) $(selector).html(_helper_html_wrap(msg, btnHtml))

  // --- [api] run importer function
  if (res.status <= 201) {
    http_post("/_execute", `${cockpitPath}.importer_import`, null, null, (self, status, data, params) => {
      if (status === 200) {
        msg = 'Import finished successful!'
        $(selector).html(_helper_html_wrap(msg, btnHtml))
      } else {
        msg = `Failed running importer.import!`, status, data, params
        $(selector).html(_helper_html_wrap(msg, btnHtml))
      }
    })
  }

  $('#importer-cockpit-next').html(`<button type="button" class="btn btn-primary" data-dismiss="modal" id="importer-cockpit-next">Close</button>`);
}

// --- Approve File (STEP 2)
function cockpit_importer_preview() {
  _helper_log('cockpit_preview')
  http_post("/_execute", cockpitPath + ".importer_preview", null, null, (self, status, data, params) => {
    console.log("cockpit_preview", status);
  });
}

// --- closes the cockpit
function cockpit_close() {
  _helper_log('cockpit_close')
  cockpiteventSource.close();
}

function _helper_log(logText) {
  const length = logText.length + 4
  let header = ''
  for (var i = 0, len = length; i < len; i++) {
    header = `${header}=`
  }
  console.log(header)
  console.log(`| ${logText} |`)
  console.log(header)
}

// --- _helper_modal_activate_step_no
function _helper_modal_activate_step_no(stepNo) {
  activePanelIndex = stepNo
  const newActivePane = "tabpane" + stepNo
  const tabId = 'tab' + stepNo
  $('#' + tabId).click()
  $("#myTabContent").children('div').each(function (index, el) {
    const childStepNo = $(el).attr("id")
    const tabPaneId = 'tabpane' + stepNo
    const tabId = 'tab' + stepNo
    if (newActivePane === childStepNo) {
      // --- activate actual pane
      $('#' + tabId).removeClass('disabled')
      $('#' + tabId).click()
    } else {
      // --- deactivate all other panes
      $('#' + tabId).addClass('disabled')
    }
  })
}

// --- create a slug from a given string
function _helper_slugify(inputStr) {
  return inputStr
    .toLowerCase()
    .replace(/[^\w ]+/g, '')
    .replace(/ +/g, '-')
}

// --- preformat html
function _helper_html_wrap(msg, wrap) {
  return `${wrap}<div class="text-center">${msg}<div>${wrap}`
}

// --- ensures that the corresponding checkboxes have the right value
// - when checkbox time is set, all other time checkboxes will be removed 
// - the corresponding import checkbox is deactivated
function _helper_checkbox_time(fieldId) {
  const clickedElId = 'importer-field-time-' + fieldId
  // make sure that we do not import time fields
  $("#importer-field-name-" + fieldId).prop('checked', false)
  $("input[id^=importer-field-time-]").each(function (index, el) {
    const elId = $(el).attr('id')
    if (elId !== clickedElId) {
      $(el).removeAttr('checked')
      $(el).prop('checked', false)
      $(el).attr('checked', false)
    }
  })
}

function clickonTab(tabIndex) {
  switch (activePanelIndex) {
    case 1:
      if (tabIndex == 2)
        cockpit_importer_2_approve_file();
      break;
    case 2:
      if (tabIndex == 1)
        cockpit_importer_1_choose_file();
      else if (tabIndex == 3)
        cockpit_importer_3a_define_header_file_contains_header();
      break;
    case 3:
      if (tabIndex == 1)
        cockpit_importer_1_choose_file();
      else if (tabIndex == 2)
        cockpit_importer_2_approve_file();
      else if (tabIndex == 4)
        cockpit_importer_5_finish_import();
      break;
    case 4:
      break;
  }
}