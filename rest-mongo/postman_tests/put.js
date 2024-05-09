pm.test("Status code is 200 or 404", function () {
  pm.expect(pm.response.code).to.be.oneOf([200, 404]);
});

pm.test("Successful update response message", function () {
  if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.expect(jsonData.message).to.eql("Task updated successfully");
  }
});

pm.test("Task not found or no changes made", function () {
  if (pm.response.code === 404) {
    var jsonData = pm.response.json();
    pm.expect(jsonData.error).to.eql("Task not found or no changes were made");
  }
});
