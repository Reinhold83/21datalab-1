//var settingPath = "root.visualization.selfservice0.contextMenuSettings";
var settingPath = "root.system.globalSettings";

var defaultJsonValidation = {
    "type": "null",     // string, integer, boolean, null, array
    "description": "Please add json validation",
};

/*
    Json Schema Types
    {"type": "integer","minimum": 0,"maximum": 150}
    {"type": "float","minimum": 0,"maximum": 150}
    {"type": "boolean"}
    {"enum": ["Street", "Avenue", "Boulevard"] }
*/

function getReferenceLeaves(settingPath, name) {
    var path = settingPath + "." + name;

    return new Promise(resolve => {
        http_post('_getleaves', path, null, null, function (obj, status, data, params) {
            var msgs = JSON.parse(data);

            if (msgs.length == 0)
                resolve("none");
            resolve(msgs);
        });
    });
}

async function createSettingWidgets(table, settingPath, entries, branchData) {
    for (var i in entries) {
        // var i = 0; {
        var entry = entries[i];
        // var referenceLeaves[0] = branchData[entry.name]['.properties'].leavesValues[0];
        var referenceLeaves = await getReferenceLeaves(settingPath, entry.name);
        //make a row
        var row = document.createElement("div");
        row.className = "form-group row mb-2";
        row.setAttribute("data-toggle", "tooltip");
        row.setAttribute("data-placement", "bottom");
        row.setAttribute("title", "There was some errors loading the data...");

        // label div
        var label = document.createElement("label");
        label.className = "col-2";
        label.innerHTML = entry.name;

        if (referenceLeaves != undefined && referenceLeaves != null && referenceLeaves != "none") {
            // input div
            var input;
            var jsonValidation = referenceLeaves[0].jsonValidation;
            // change input field according to the jsonValidation schema
            if (jsonValidation == undefined) {
                input = document.createElement("input");

                input.value = referenceLeaves[0].value;
                input.setAttribute("data-type", "string");
                input.setAttribute("path", entry.name);
            } else if (jsonValidation.enum != undefined) {
                var input = document.createElement("SELECT");

                var inner = "";
                var possibleValues = jsonValidation.enum;
                for (var i in possibleValues) {
                    inner = inner + "<option>" + possibleValues[i] + "</option>";
                }
                input.innerHTML = inner;
                input.value = referenceLeaves[0].value;
                input.setAttribute("data-type", jsonValidation.type);
                input.setAttribute("path", entry.name);
            } else if (jsonValidation.type == undefined) {
                input = document.createElement("input");

                input.value = referenceLeaves[0].value;
                input.setAttribute("data-type", "string");
                input.setAttribute("path", entry.name);
            } else if (jsonValidation.type == "integer") {
                input = document.createElement("input");

                input.value = referenceLeaves[0].value;
                input.setAttribute("type", "range");

                input.setAttribute("min", jsonValidation.minimum);
                input.setAttribute("max", jsonValidation.maximum);
                input.setAttribute("data-type", jsonValidation.type);
                input.setAttribute("path", entry.name);
            } else if (jsonValidation.type == "boolean") {
                input = document.createElement("input");

                input.setAttribute("type", "checkbox");
                if (referenceLeaves[0].value == 'true' || referenceLeaves[0].value == true)
                    input.setAttribute("checked", true);
                input.setAttribute("data-type", jsonValidation.type);
                input.setAttribute("path", entry.name);
            } else {
                input = document.createElement("input");

                input.value = referenceLeaves[0].value;
                input.setAttribute("data-type", "string");
                input.setAttribute("path", entry.name);
            }

            if (jsonValidation == undefined) {
                input.className = "form-control col-7";
            } else if (jsonValidation.type == "integer") {
                input.className = "form-control col-6 slider";
            } else if (jsonValidation.type == "boolean") {
                input.className = "col-7 form-check-input";
                input.style.position = "relative";
                input.style.marginLeft = "0px";
            } else {
                input.className = "form-control col-7";
            }

            // add browse Path 
            var browsePath = document.createElement("input");
            browsePath.className = "form-control col-7 hidden";

            var browsePathValue = "";
            for (var i = 0; i < referenceLeaves.length; i++)
                browsePathValue += (i == 0 ? "" : ",") + referenceLeaves[i].browsePath;
            browsePath.value = browsePathValue;
            browsePath.setAttribute("type", "hidden");

            // apply button
            var btn = document.createElement("BUTTON");   // Create a <button> element
            btn.className = "btn btn-primary btn-sm col-1 ml-2";
            btn.id = "apply-" + entry.id;
            btn.innerHTML = 'Apply';

            if (jsonValidation == undefined && jsonValidation.description == undefined)
                row.setAttribute("title", "Please add description in the json validaiton schema");
            else
                row.setAttribute("title", jsonValidation.description);

            if (jsonValidation == undefined)
                row.append(label, input, browsePath, btn);
            else if (jsonValidation.type == "integer") {
                var sliderValue = document.createElement("div");
                sliderValue.className = "col-1";
                sliderValue.style.textAlign = "center";
                sliderValue.style.paddingTop = "6px";
                input.style.paddingLeft = "0px";
                input.style.paddingRight = "0px";
                sliderValue.innerHTML = referenceLeaves[0].value;
                row.append(label, input, sliderValue, browsePath, btn);
            } else {
                row.append(label, input, browsePath, btn);
            }
            table.append(row);
        }
    }
}

function createSettingWidgetsSync(table, settingPath, entries, branchDataArray) {
    for (var i in entries) {
        // var i = 0; {
        var entry = entries[i];
        var branchData = branchDataArray[entry.name]['.properties'];
        var branchId = branchData.leavesIds[0];
        var referenceLeaves = branchData.leavesProperties[branchId];
        //make a row
        var row = document.createElement("div");
        row.className = "form-group row mb-2";
        row.setAttribute("data-toggle", "tooltip");
        row.setAttribute("data-placement", "bottom");
        row.setAttribute("title", "There was some errors loading the data...");

        // label div
        var label = document.createElement("label");
        label.className = "col-2 mr-3 mt-2";
        label.innerHTML = entry.name;

        if (referenceLeaves != undefined && referenceLeaves != null && referenceLeaves != "none") {
            // input div
            var input;
            var jsonValidation = referenceLeaves.jsonValidation;
            // change input field according to the jsonValidation schema
            if (jsonValidation == undefined) {
                // input widget
                input = document.createElement("input");
                input.setAttribute("globalSettings",true);
                input.value = referenceLeaves.value;
                input.setAttribute("data-type", "string");
                input.setAttribute("path", entry.name);
            } else if (jsonValidation.enum != undefined) {
                // when enum has value, it is a select widget
                var input = document.createElement("SELECT");
                input.setAttribute("globalSettings",true);
                var inner = "";
                var possibleValues = jsonValidation.enum;
                for (var i in possibleValues) {
                    var optionValue = typeof possibleValues[i] + ":" + possibleValues[i];
                    inner = inner + "<option value='" + optionValue + "'>" + possibleValues[i] + "</option>";
                }
                input.innerHTML = inner;
                input.value = typeof referenceLeaves.value + ":" + referenceLeaves.value;
                input.setAttribute("data-type", "enum");
                input.setAttribute("path", entry.name);
                input.setAttribute("globalSettings",true);
            } else if (jsonValidation.type == undefined) {
                // input widget
                input = document.createElement("input");
                input.setAttribute("globalSettings",true);

                input.value = referenceLeaves.value;
                input.setAttribute("data-type", "string");
                input.setAttribute("path", entry.name);
            } else if (jsonValidation.type == "integer") {
                input = document.createElement("input");
                input.setAttribute("globalSettings",true);
                input.setAttribute("path", entry.name);
                if (jsonValidation.minimum == undefined || jsonValidation.maximum == undefined) {
                    input.setAttribute("data-type", "number integer");
                    input.setAttribute("type", "number");
                    input.setAttribute("step", "1");
                } else {
                    input.setAttribute("type", "range");
                    input.setAttribute("min", jsonValidation.minimum);
                    input.setAttribute("max", jsonValidation.maximum);
                    input.setAttribute("data-type", jsonValidation.type);
                }
                input.value = referenceLeaves.value;
            } else if (jsonValidation.type == "float") {
                input = document.createElement("input");
                input.setAttribute("globalSettings",true);
                input.setAttribute("path", entry.name);
                if (jsonValidation.minimum == undefined || jsonValidation.maximum == undefined) {
                    input.setAttribute("data-type", "number float");
                    input.setAttribute("type", "number");
                } else {
                    input.setAttribute("type", "range");
                    input.setAttribute("step", "0.01");
                    input.setAttribute("slider-precision", "0.01");
                    input.setAttribute("min", jsonValidation.minimum);
                    input.setAttribute("max", jsonValidation.maximum);
                    input.setAttribute("data-type", jsonValidation.type);
                }
                input.value = referenceLeaves.value;
            } else if (jsonValidation.type == "boolean") {
                input = document.createElement("input");
                input.setAttribute("globalSettings",true);

                input.setAttribute("type", "checkbox");
                if (referenceLeaves.value == 'true' || referenceLeaves.value == true)
                    input.setAttribute("checked", true);
                input.setAttribute("data-type", jsonValidation.type);
                input.setAttribute("path", entry.name);
            } else {
                input = document.createElement("input");
                input.setAttribute("globalSettings",true);

                input.value = referenceLeaves.value;
                input.setAttribute("data-type", "string");
                input.setAttribute("path", entry.name);
            }

            if (jsonValidation == undefined) {
                input.className = "form-control col-7";
            } else if (jsonValidation.enum != undefined)
                // input.className = "form-control col-8 slider";
                input.className = "form-control col-7 slider";
            else if (jsonValidation.type == "integer" || jsonValidation.type == "float") {
                input.className = "form-control col-7 slider";
            } else if (jsonValidation.type == "boolean") {
                input.className = "col-7 form-check-input";
                // input.className = "col-8 form-check-input";
                input.style.position = "relative";
                input.style.marginLeft = "0px";
            } else {
                input.className = "form-control col-7";
            }

            // add browse Path 
            var browsePath = document.createElement("input");
            input.setAttribute("globalSettings",true);
            browsePath.className = "form-control col-7 hidden";

            var browsePathValue = "";
            for (var i = 0; i < referenceLeaves.length; i++)
                browsePathValue += (i == 0 ? "" : ",") + referenceLeaves[i].browsePath;
            browsePath.value = browsePathValue;
            browsePath.setAttribute("type", "hidden");

            if (jsonValidation == undefined || jsonValidation.description == undefined)
                row.setAttribute("title", "Please add description in the json validaiton schema");
            else
                row.setAttribute("title", jsonValidation.description);

            if (jsonValidation == undefined) {
                // apply button
                var btn = document.createElement("BUTTON");   // Create a <button> element
                btn.setAttribute("globalSettings",true);
                btn.className = "btn btn-primary btn-sm w-100 h-100";
                btn.id = "apply-" + entry.id;
                btn.innerHTML = 'Apply';

                var buttonWrapper = document.createElement("div");
                buttonWrapper.setAttribute("globalSettings",true)
                buttonWrapper.className = "col-1 pl-2 pr-0 button-wrapper";
                buttonWrapper.append(label, input, browsePath, btn);
                row.append(label, input, browsePath, buttonWrapper);
            }
            else if (jsonValidation.enum != undefined) {
                row.append(label, input, browsePath);
            } else if (input.getAttribute("data-type") == "string" || input.getAttribute("data-type") == "number float" || input.getAttribute("data-type") == "number integer") {
                // apply button
                var btn = document.createElement("BUTTON");   // Create a <button> element
                btn.setAttribute("globalSettings",true);
                btn.className = "btn btn-primary btn-sm w-100 h-100";
                btn.id = "apply-" + entry.id;
                btn.innerHTML = 'Apply';

                var buttonWrapper = document.createElement("div");
                buttonWrapper.setAttribute("globalSettings",true);
                buttonWrapper.className = "col-1 pl-2 pr-0 button-wrapper";
                buttonWrapper.append(label, input, browsePath, btn);
                row.append(label, input, browsePath, buttonWrapper);
            } else if (jsonValidation.type == "integer" || jsonValidation.type == "float") {
                var sliderValue = document.createElement("div");
                sliderValue.className = "col-1";
                sliderValue.style.textAlign = "center";
                sliderValue.style.paddingTop = "6px";
                input.style.paddingLeft = "0px";
                input.style.paddingRight = "0px";
                sliderValue.innerHTML = referenceLeaves.value;
                row.append(label, input, sliderValue, browsePath);
            } else {
                row.append(label, input, browsePath);
            }
            table.append(row);
        }
    }
}

$(document).on("click input", ".slider", function () {
    //do stuff
    if (!this.hasAttribute("globalSettings")) return; //the callback is too general, we only look at "our" controls
    var parent = $(this).parent();
    var children = parent.children();
    var value = children[1].value;
    children[2].innerHTML = value;
});

$(document).on("change", ".slider", function () {
    //save slider value when changes
    if (!this.hasAttribute("globalSettings")) return; //the callback is too general, we only look at "our" controls
    saveSettingValue(this);
});

$(document).on("change input", "SELECT", function () {
    //save enum value when changes
    if (!this.hasAttribute("globalSettings")) return; //the callback is too general, we only look at "our" controls
    saveSettingValue(this);


});

$(document).on("input change", "input:checkbox", function () {
    //save enum value when changes
    if (!this.hasAttribute("globalSettings")) return; //the callback is too general, we only look at "our" controls
    saveSettingValue(this);
});

$(document).on("click", ".button-wrapper", function () {
    //save enum value when changes
    if (!this.hasAttribute("globalSettings")) return; //the callback is too general, we only look at "our" controls
    saveSettingValue(this);
});

function saveSettingValue(target) {
    var parent = $(target).parent();
    var children = parent.children();
    var value = children[1].value;

    var dataType = children[1].getAttribute("data-type");

    if (dataType == "enum") {
        var type = value.split(":")[0];
        if (type == "number") {
            console.log("type is number");
            value = parseFloat(value.split(":")[1]);
        } else {
            value = value.split(":")[1];
        }
    } else if (dataType == "boolean")
        value = $(children[1])[0].checked;
    else if (dataType == "integer" || dataType == "number integer")
        value = parseInt(value);
    else if (dataType == "float" || dataType == "number float")
        value = parseFloat(value);
    var path = settingPath + "." + children[1].getAttribute("path");

    // get the children of reference, then save the new value to each of them.
    http_post('_getleaves', path, null, null, function (obj, status, data, params) {
        var msgs = JSON.parse(data);

        for (var i = 0; i < msgs.length; i++) {
            var query = [
                {
                    "browsePath": msgs[i].browsePath,
                    "value": value
                }];
            http_post("/setProperties", JSON.stringify(query));
        }
    });
}

function initialize_settings() {
    console.log("initialize settings");

    http_post("/_getbranchpretty", JSON.stringify(settingPath), null, null, function (obj, status, data, params) {
        var branchData = JSON.parse(data);

        http_post("_get", JSON.stringify([settingPath]), null, null, function (obj, status, data, params) {
            var table = $('#settingContainer');
            if (status == 200) {
                /*create the table*/
                var msgs = JSON.parse(data);

                if ((msgs[0] == null) || (msgs[0].children.length == 0)) {
                    table.empty();
                }
                else {
                    //we have at least one entry
                    table.empty();
                    createSettingWidgetsSync(table, settingPath, msgs[0].children, branchData);
                }
            }
        });
    });
}

/**
 * Check if the node has jsonvalidation property
 */
function initSettingJsonValidation() {
    http_post("_get", JSON.stringify([settingPath]), null, null, function (obj, status, data, params) {
        var entries = JSON.parse(data);

        if ((entries[0] == null) || (entries[0].children.length == 0)) {
            return;
        }

        for (var i in entries[0].children) {
            var entry = entries[0].children[i];
            var path = settingPath + "." + entry.name;

            http_post('_getleaves', path, null, null, function (obj, status, data, params) {
                var msgs = JSON.parse(data);
                if (msgs.length == 0)
                    return;
                var properties = msgs[0];
                if (properties['jsonValidation'] == undefined) {
                    // add default json validation
                    var query = [
                        {
                            "browsePath": properties.browsePath, "jsonValidation": {}
                        }
                    ];
                    http_post("/setProperties", JSON.stringify(query));
                }
            });
        }
    });
}