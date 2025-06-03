document.getElementById("upload-zip-btn").addEventListener("click", function () {
    const fileInput = document.getElementById("zipInput");
    const result = document.getElementById("uploadZipResult");

    if (fileInput.files.length === 0) {
        result.textContent = "请先选择一个 .zip 文件";
        return;
    }

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    fetch("/upload/images/", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        result.textContent = JSON.stringify(data, null, 2);
    })
    .catch(error => {
        result.textContent = "上传失败: " + error;
    });
});
