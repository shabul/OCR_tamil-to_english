var uploads_json = {};
var results_json = {}

$("#pdf-input").on('change', function(e){
    var fileName = e.target.files[0].name;
    $("#pdf-file-name").text(fileName);
});

$("#file-upload-form").on("submit", function(e){
    e.preventDefault();
    // console.log("File upload");
    var formData = new FormData();
    // console.log($("#pdf-input"));
    formData.append("pdf", $("#pdf-input")[0].files[0]);
    $.ajax({
        method: "POST",
        url: "/upload",
        data: formData,
        processData: false,
        contentType: false,
        success: function(){
            alert('Upload Successful!');
        },
    });
});

function closeModal(){
    $('#result-modal').removeClass('is-active');
}

function updatePageContent(upload_id, page_no){
    upload_details = results_json[upload_id];
    console.log(upload_details);
    results = upload_details["results"];
    if(page_no >= 0 && page_no < results.length){
        page_results = results[page_no];
        $('#result-modal').attr('data-page-no', page_no);
        console.log(upload_id, page_no);
        extracted_text = page_results['extracted_text'];
        editable_text = page_results['editable_text'];
        // console.log(extracted_text);
        $("#result-modal-page-no").text(`Page: ${page_no}`);
        $("#result-modal-editable").val(editable_text);
    }
}

function nextResultPage(){
    upload_id = $('#result-modal').attr('data-upload-id');
    page_no = $('#result-modal').attr('data-page-no');
    page_no = parseInt(page_no);
    updatePageContent(upload_id, page_no+1);
}

function prevResultPage(){
    upload_id = $('#result-modal').attr('data-upload-id');
    page_no = $('#result-modal').attr('data-page-no');
    page_no = parseInt(page_no);
    updatePageContent(upload_id, page_no-1);
}

function saveChangesButton(){
    upload_id = $('#result-modal').attr('data-upload-id');
    page_no = $('#result-modal').attr('data-page-no');
    page_no = parseInt(page_no);
    edited_text = $("#result-modal-editable").val();
    $.ajax({
        url: '/uploads/updateText',
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json',
        success: function (data) {
            alert('Updated Successfully!');
            delete results_json[upload_id];
            updateTable();
            closeModal();
        },
        error: function(){
            alert(" An error occured, please try again");
        },
        data: JSON.stringify({
            upload_id: upload_id,
            page_no: page_no,
            edited_text: edited_text
        })
    })
}

function saveChanges(){
    upload_id = $('#result-modal').attr('data-upload-id');
    page_no = $('#result-modal').attr('data-page-no');
    page_no = parseInt(page_no);
    edited_text = $("#result-modal-editable").val();
    $.ajax({
        url: '/uploads/updateText',
        type: 'POST',
        dataType: 'json',
        contentType: 'application/json',
        data: JSON.stringify({
            upload_id: upload_id,
            page_no: page_no,
            edited_text: edited_text
        })
    })
}

function showLoader() {

}

function showResults(e){
    upload_id = $(e).attr("data-upload-id");
    $('#result-modal').attr('data-upload-id', upload_id);
    $('#result-modal').attr('data-page-no', 0);
    $('#download-button').attr('href', `/download/${upload_id}`)
    $('#result-modal-title').text(`Upload: ${upload_id}`)
    $('#result-modal').addClass('is-active');
    if(results_json.hasOwnProperty(upload_id)){
        updatePageContent(upload_id, 0);
    }else{
        showLoader();
        $.ajax({
            xhr: function() {
                $("#results-content").hide();
                $("#progress-bar-wrapper").show();
                var xhr = new window.XMLHttpRequest();
        
               // Download progress
               xhr.addEventListener("progress", function(evt){
                   if (evt.lengthComputable) {
                       var percentComplete = (evt.loaded / evt.total) * 100;
                       // Do something with download progress
                       $("#progress-bar").attr("value", percentComplete);
                   }
               }, false);
               return xhr;
            },
            method: "GET",
            url: `/uploads/${upload_id}`,
            success: function(data){
                $("#progress-bar-wrapper").hide();
                $("#results-content").show();
                $("#progress-bar").attr("value", 0);
                upload_id = data['id'];
                results_json[upload_id] = {
                    results: data['results']
                }
                embed_height = $("#result-modal-body").height() * 0.8;
                embed_width = $("#result-modal-editable").width() * 0.95;
                $("#result-modal-extracted").html(`<embed src="/viewPDF/${upload_id}" height=${embed_height} width=${embed_width}></embed>`);
                updatePageContent(upload_id, 0);
            }
        })
    }
}

function updateTable(){
    $.ajax({
        method: "GET",
        url: "/uploads",
    }).done((data) => {
        var uploadsTable = $("#uploads-table-body")
        uploads_json = Object.assign(uploads_json, data);
        htmlContent = ""

        Object.keys(data).forEach(function(upload_id) {
            element = data[upload_id]
            var status = element.status;
            if(element.done){
                status = `<button data-upload-id='${upload_id}'type='button' class='btn btn-primary' onclick='showResults(this)'>View Results</button>`;
            }
            htmlContent += `<tr>
                <td>${upload_id}</td>
                <td>${element.upload_time}</td>
                <td>${status}</td>
            </tr>`
        });
        uploadsTable.html(htmlContent);
    });
}

$(document).ready(function() {
    updateTable();
    setInterval(updateTable, 1000);
} );
