import nopecha







nopecha.api_key = 'I-H7AG500SGFEN'

# Call the Recognition API
clicks = nopecha.Recognition.solve(
    type='funcaptcha',
    task="Pick the mouse that can't reach the cheese",
    image_data=['/9j/2wCEAAoHBwgHBgoI...']
)

# Print the grids to click
print(clicks)