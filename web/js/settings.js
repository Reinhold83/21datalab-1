var settingPath = "root.visualization.selfservice0.contextMenuSettings";
// var settingPath = "root.system.globalSettings";
var defaultJsonValidation = {
    "type": "enum",     // boolean, text, enum, number
    "description": "Default json validation schema",
    min: 0,
    max: 100,
    enum: "first item,second item,etc"
};

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
            var jsonValidation = JSON.parse(referenceLeaves[0].jsonValidation);
            // change input field according to the jsonValidation schema
            if (jsonValidation.type == "boolean") {
                input = document.createElement("input");
                input.setAttribute("type", "checkbox");
                if (referenceLeaves[0].value == 'true' || referenceLeaves[0].value == true)
                    input.setAttribute("checked", true);
            } else if (jsonValidation.type == "number") {
                input = document.createElement("input");
                input.setAttribute("type", "range");
                input.setAttribute("min", jsonValidation.min);
                input.setAttribute("max", jsonValidation.max);

                // Add tooltip to show value
                // row.setAttribute("data-toggle", "tooltip");
                // row.setAttribute("data-placement", "bottom");
                // input.setAttribute("title", "Min Value : " + referenceLeaves[0].min + " Max Value : " + referenceLeaves[0].max);
            } else if (jsonValidation.type == "enum") {
                var input = document.createElement("SELECT")
                var inner = "";
                var possibleValues = jsonValidation.enum.toString().split(",");
                for (var i in possibleValues) {
                    inner = inner + "<option>" + possibleValues[i] + "</option>";
                }
                input.innerHTML = inner;
            } else {
                input = document.createElement("input");
                input.value = referenceLeaves[0].value;
            }
            input.className = "form-control col-7";

            // add browse Path 
            var browsePath = document.createElement("input");
            browsePath.className = "form-control col-7 hidden";

            var browsePathValue = "";
            for (var i=0 ; i<referenceLeaves.length ; i++)
                browsePathValue += (i == 0 ? "" : ",") + referenceLeaves[i].browsePath;
            browsePath.value = browsePathValue;
            browsePath.setAttribute("type", "hidden");

            // apply button
            var btn = document.createElement("BUTTON");   // Create a <button> element
            btn.className = "btn btn-primary btn-sm col-1 ml-2";
            btn.id = "apply-" + entry.id;
            btn.innerHTML = 'Apply';
            btn.onclick = saveSettingValue;

            row.setAttribute("title", jsonValidation.description);
            row.append(label, input, browsePath, btn);
            table.append(row);
        }
    }
}

function saveSettingValue(event) {
    var parent = $(event.target).parent();
    var children = parent.children();
    var value = children[1].value;
    var browsePath = children[2].value.split(",");
    console.log(browsePath);
    console.log(value);
    return;
    var query = [
        {
            "browsePath": browsePath,
            "value": JSON.stringify(value)
        }];
    http_post("/setProperties", JSON.stringify(query));
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

                    createSettingWidgets(table, settingPath, msgs[0].children, branchData);
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
                // if (properties['jsonValidation'] == undefined) 
                {
                    // add default json validation
                    var query = [
                        { "browsePath": properties.browsePath, "jsonValidation": JSON.stringify(defaultJsonValidation) }
                    ];
                    http_post("/setProperties", JSON.stringify(query));
                }
            });
        }
    });
}