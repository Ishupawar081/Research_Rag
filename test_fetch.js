const fs = require('fs');

async function test() {
    const formData = new FormData();
    formData.append("file", new Blob(["dummy content"], { type: "application/pdf" }), "dummy.pdf");
    
    const response = await fetch("http://localhost:8000/upload", {
        method: "POST",
        headers: {
            "Authorization": "Bearer FAKE_TOKEN"
        },
        body: formData,
    });
    console.log(response.status, response.statusText);
    const text = await response.text();
    console.log(text);
}
test();
