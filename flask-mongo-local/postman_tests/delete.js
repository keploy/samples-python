pm.test("Status code is 200 or 404", function () {
  pm.expect(pm.response.code).to.be.oneOf([200, 404]);
});

pm.test("Successful deletion response message", function () {
  if (pm.response.code === 200) {
    var jsonData = pm.response.json();
    pm.expect(jsonData.message).to.eql("Task deleted successfully");
  }
});

pm.test("Task not found", function () {
  if (pm.response.code === 404) {
    var jsonData = pm.response.json();
    pm.expect(jsonData.error).to.eql("Task not found");
  }
});
