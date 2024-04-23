pm.test("Status code is 201", function () {
  pm.response.to.have.status(201);
});

pm.test("Response contains task ID", function () {
  var jsonData = pm.response.json();
  pm.expect(jsonData).to.have.property("id");
  pm.expect(jsonData.id).to.not.be.empty;
});

pm.test("Response message is correct", function () {
  var jsonData = pm.response.json();
  pm.expect(jsonData.message).to.eql("Task created successfully");
});
