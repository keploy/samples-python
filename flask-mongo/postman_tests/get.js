pm.test("Status code is 200", function () {
  pm.response.to.have.status(200);
});

pm.test("Response is an array", function () {
  var jsonData = pm.response.json();
  pm.expect(jsonData.tasks).to.be.an("array");
});

pm.test("Each task has an id, title, and description", function () {
  var jsonData = pm.response.json();
  jsonData.tasks.forEach(function (task) {
    pm.expect(task).to.have.property("id");
    pm.expect(task).to.have.property("title");
    pm.expect(task).to.have.property("description");
  });
});
