document.addEventListener("DOMContentLoaded", function () {
    const fileInput = document.getElementById("fileInput");
    const uploadBtn = document.getElementById("upload-btn");
    const resultBox = document.getElementById("uploadResult");

    uploadBtn.addEventListener("click", async function () {
        const files = fileInput.files;
        if (files.length === 0) {
            resultBox.textContent = "请先选择至少一个文件。";
            return;
        }

        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append("   files", files[i]);  // 👈 多文件字段名统一为“files”
        }

        resultBox.textContent = "上传中，请稍候...";

        try {
            const response = await fetch("/api/upload/file/", {
                method: "POST",
                body: formData,
            });

            const data = await response.json();

            if (response.ok && data.success) {
                resultBox.textContent = `✅ 上传成功！\n\n📥 导入数量：${data.inserted}\n⏭ 跳过数量：${data.skipped}\n🆔 导入ID：${data.ids.join(", ")}`;
            } else {
                resultBox.textContent = `❌ 上传失败: ${data.error || JSON.stringify(data)}`;
            }
        } catch (error) {
            resultBox.textContent = "上传失败: " + error.message;
        }
    });
});
