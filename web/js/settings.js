var settingPath = "root.visualization.selfservice0.contextMenuSettings";

function getReferenceValue(settingPath, name) {
    var path = settingPath + "." + name;

    return new Promise(resolve => {
        http_post('_getleaves', path, null, null, function (obj, status, data, params) {
            var msgs = JSON.parse(data);
            if (msgs.length == 0)
                resolve("none");
            resolve(msgs[0].value);
        });
    });
}

async function createSettingWidgets(table, settingPath, entries) {
    for (var i in entries) {
        var entry = entries[i];
        var referenceValue = await getReferenceValue(settingPath, entry.name);
        //make a row
        var row = document.createElement("div");
        row.className = "form-group row mb-2";

        // label div
        var label = document.createElement("label");
        label.className = "col-2";
        label.innerHTML = entry.name;

        if (referenceValue != "none") {
            // input div
            var input = document.createElement("input");
            input.className = "form-control col-7";
            input.value = referenceValue;

            // apply button
            var btn = document.createElement("BUTTON");   // Create a <button> element
            btn.className = "btn btn-primary btn-sm col-1 ml-2";
            btn.id = "apply-" + entry.id;
            btn.innerHTML = 'Apply';
            // btn.onclick = select_view;

            row.append(label, input, btn);
            table.append(row);
        }
    }
}


function initialize_settings() {
    console.log("initialize settings");

    http_post("_get", JSON.stringify(["root.system.globalSettings.bins"]), "root.system.globalSettings", null, function (isLast, status, data, params) {
        // console.log(status);
        // console.log(params);
        // console.log(data);
    });
    // var settingPath = "root.system.globalSettings";
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

                //         var tim = document.createElement("div");
                //         tim.className = "col-4";
                //         tim.innerHTML = "Date/Time";
                //         var act = document.createElement("div");
                //         act.className = "col-3";
                //         act.innerHTML = "Action";
                //         row.append(msgDiv,tim,act);
                //         table.append(row);

                createSettingWidgets(table, settingPath, msgs[0].children);
                // var i = 0;
                // while(i < msgs[0].children.length){
                //     var entry = msgs[0].children[i];
                //     i++;
                //     // createReferenceWidget(settingPath, entry).then((row) => { table.append(row); i++;});
                // }
                // 
                // for (var i = 0; ; ) {
                //     var entry = msgs[0].children[i];

                //     createReferenceWidget(settingPath, entry);
                // }
            }
        }

        //             var timeDiv = document.createElement("div");
        //             timeDiv.className = "col-4";
        //             if ((entry.value!=null) && ("time" in entry.value))
        //             {
        //                 timeDiv.innerHTML = entry.value.time;
        //             }
        //             else
        //             {
        //                 timeDiv.innerHTML = " -unknown time-";
        //             }


        //             var msgDiv = document.createElement("div");
        //             msgDiv.className = "col-5";
        //             msgDiv.innerHTML = entry.name;


        //             let buttonDiv1 = document.createElement("div");
        //             buttonDiv1.className = "col-3";
        //             let buttonDiv = document.createElement("div")
        //             buttonDiv.className = "btn-group";






        //             var savebtn = document.createElement("BUTTON");   // Create a <button> element
        //             savebtn.className = "btn btn-secondary";
        //             savebtn.id = "saveView-"+entry.name;
        //             savebtn.innerHTML = '<i class="fas fa-save"></i>';
        //             savebtn.onclick = save_view;
        //             let span = document.createElement("span");
        //             span.innerHTML = "&nbsp;&nbsp;"
        //             buttonDiv.append(span);
        //             buttonDiv.append(savebtn);


        //             var delbtn =  document.createElement("BUTTON");   // Create a <button> element
        //             delbtn.className = "btn btn-secondary";
        //             delbtn.id = "deleteView-"+entry.name;
        //             delbtn.innerHTML = '<i class="far fa-trash-alt"></i>';
        //             delbtn.onclick = delete_view;
        //             let span2 = document.createElement("span");
        //             span2.innerHTML = "&nbsp;&nbsp;"
        //             buttonDiv.append(span2);
        //             buttonDiv.append(delbtn);

        //             buttonDiv1.append(buttonDiv);

        //             row.append(msgDiv,timeDiv,buttonDiv1);
        //             //row.appendChild(msgDiv);
        //             table.append(row);
        //         }



        //     }
        // }
        // else
        // {

        //     table.empty();
        // }


        // // at the very end add the new entry button
        // var addViewDiv = document.createElement("div");
        // addViewDiv.className = "col-3";

        // var addViewBtn = document.createElement("BUTTON");   // Create a <button> element
        // addViewBtn.className = "btn btn-secondary";
        // addViewBtn.id = "addView";
        // addViewBtn.innerHTML = '<i class="fas fa-plus"></i>';
        // addViewBtn.onclick = add_view;
        // addViewDiv.append(addViewBtn);
        // table.append(addViewDiv);
    });
}




