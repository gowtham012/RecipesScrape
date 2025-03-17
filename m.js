// Assuming categoriesDataset is an array of your category objects
const validRecipeLinks = [];

categoriesDataset.forEach(category => {
  if (Array.isArray(category.recipes)) {
    category.recipes.forEach(recipe => {
      // Check that all required fields exist and are not empty
      if (
        recipe.title &&
        recipe.description &&
        recipe.image &&
        recipe.ingredients &&
        recipe.instructions &&
        recipe.url // assuming you have a field with the recipe link
      ) {
        validRecipeLinks.push(recipe.url);
      }
    });
  }
});

console.log('Valid recipe links:', validRecipeLinks);
