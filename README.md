# Admin Base App

The `admin_base` app serves as the foundational layer for all applications within the Token's United framework. It provides essential components and configurations that ensure seamless functionality across the website. This app acts as the backbone for other apps, offering a unified template and shared resources.

## Description
The `admin_base` app is designed to facilitate the core functionalities needed for managing the website's backend. It includes middleware that operates during site loading, manages caching mechanisms, and provides access to a centralized database containing essential information accessible by all apps. The app also features a login form for backend access and includes various backend components such as loading screens and indicators.

### Features
- **Unified Template**: All apps expand their templates from the main template provided by `admin_base`, ensuring consistency across the backend.
- **Caching Management**: Efficient caching solutions that improve website performance and loading times.
- **Centralized Database**: `general.db` contains all vital information needed by various apps, enabling easy data access.
- **Backend Components**: Includes general backend utilities like loading screens and indicators for enhanced user experience.
- **Dynamic Template Detection**: Automatically detects installed apps and adjusts its appearance accordingly.

## Compatibility
- ### **Templates**
    - **company_profile**: A core template utilized by all apps, ensuring consistent design and functionality. Template contains custom version of `admin_base` app.

## Installation

1. **Add Submodule**:
    ```bash
    git submodule add https://github.com/Yaso2Go/admin_base.git admin_base/
    ```

2. **Initialize the submodule**:
    ```bash
    git submodule init
    ```

## Technical Details

### 1. Caching
The caching system in `admin_base` is designed to enhance website performance by storing frequently accessed data. The cache is managed using Django's caching framework and is configured in the `settings.py` file. The cache is updated whenever changes are made in the backend, ensuring that users always see the most recent content. The `resetAllCaches` function in [admin_base/static/admin_base/js/cache.js](admin_base/static/admin_base/js/cache.js) is responsible for clearing cached images, CSS, and JS files, as well as session storage and service worker caches.

#### Caching Mechanism Overview

##### Client-Side Caching

1. **Cache Reset Mechanism**:
    - The `cache.js` file is responsible for managing the cache reset mechanism on the client side.
    - When the page loads, it checks for the `cache_reset` parameter in the URL.
    - If `cache_reset=true` is present, it triggers the `resetAllCaches` function to clear various caches (images, session storage, service worker caches).
    - After clearing the caches, it reloads the page to apply the changes and bypass the cache.
    - The URL is then cleaned up to remove the `cache_reset` parameter.

2. **Cache Busting**:
    - The `resetAllCaches` function appends a timestamp to image URLs to force a reload and bypass the browser cache.

##### Server-Side Caching

1. **Cache Update Middleware**:
    - The `CacheUpdateMiddleware` in `middleware.py` handles cache updates on the server side.
    - It intercepts all GET requests and checks if the cache needs to be updated by comparing the cache version stored in the database with the version stored in the user's session.
    - If the versions do not match, it triggers a cache reset by calling the `clear_cache` management command and updates the cache version in the session.
    - The middleware then redirects the user to the same URL with the `cache_reset=true` parameter to trigger the client-side cache reset mechanism.

2. **Database Cache Versioning**:
    - The `update_content_cache_index` function in `functions.py` updates the cache version index in the database whenever content is updated.
    - This ensures that the cache version is incremented whenever there are changes to the content, prompting the middleware to trigger a cache reset for users.

##### Admin-Side Content Editing

1. **Content Updates**:
    - When an admin updates content (e.g., uploads an image), the `update_image` function in `functions.py` handles the image processing and saving.
    - The function updates the image in the specified format, removes any existing images with the same name but different formats, and updates the database with the new image path.
    - After updating the image, the `update_content_cache_index` function is called to increment the cache version index in the database.

2. **Cache Clearing**:
    - The `clear_cache` management command is called by the `CacheUpdateMiddleware` to clear the server-side cache when the cache version is updated.
    - This ensures that users receive the latest content after the admin makes changes.

##### Summary
- **Client-Side**: The `cache.js` file manages cache resetting by checking the URL for the `cache_reset` parameter, clearing caches, and reloading the page.
- **Server-Side**: The `CacheUpdateMiddleware` checks for cache version mismatches, triggers cache resets, and updates the cache version in the session.
- **Admin-Side**: Content updates by the admin trigger the `update_image` function, which processes the content and updates the cache version index in the database, prompting the middleware to clear the cache for users.

### 2. Translation

#### Translation Process Documentation

##### Initialization
The `Command` class manages the entire translation process. The `handle` method serves as the entry point for executing the command.

##### Argument Parsing
The `add_arguments` method defines command-line options for specifying the target language code and an optional argument for removing a language.

##### Handle Method

###### Start Process:
- Records the start time and extracts the target language code from the options.

###### Remove Language:
- Deletes translation files if the language is marked for removal.

###### Translation Workflow:
1. **Ensure Locale Path**: Confirms that the locale directory exists for the specified language.
2. **Check Existing Translations**: Validates whether translations for the specified language already exist.
3. **Extract Messages**: Uses the `makemessages` method to extract translatable strings from templates and generate `.po` files.
4. **Auto-Translate**: Automatically translates the `.po` files using the `translate_text_api` function.
5. **Compile Messages**: Converts `.po` files into `.mo` files using the `compilemessages` method.
6. **Add Language to Selection Box**: Adds the language to the language selection dropdown in HTML.
7. **Translate Apps**: Loops through apps and checks if they support translation by looking for a `translate.py` file and calls the `translate_app` function within the app.

Upon successful completion, the method displays a success message and the total time taken for the process.

#### Detailed Explanation of the `translation_check` Function
The `translation_check` function improves the translated text by iteratively refining it with the `str_translation_check` function until the translation meets specific criteria.

##### Function Signature
```python
def translation_check(original_translated_text, language_code):
    # ...existing code...
```

##### Key Steps

###### Initialization:
- Sets the `advanced` flag to False. This flag enables the use of a more advanced model if refinement fails.
- Initializes `trials` to track the number of refinement attempts.
- Starts the process with the provided `original_translated_text`.

###### Refinement Loop:
- Iteratively refines the translation by calling `str_translation_check`.
- Exits when the translation meets criteria (`str_pass` is True).

###### Validation:
- If `str_pass` is True, the refined translation is returned.
- If refinement fails after six attempts, the `advanced` flag is activated to use a more sophisticated bot.
- The function ensures the best possible result before returning.

#### Detailed Explanation of the `str_translation_check` Function
The `str_translation_check` function validates and refines the translated text by performing multiple checks.

##### Function Signature
```python
def str_translation_check(translated_text, language_code, advanced=False):
    # ...existing code...
```

##### Key Steps

###### Initialization:
- Chooses a primary (`llm_model`) and backup (`backup_llm_model`) model based on the `advanced` flag.

    - Curenttly as for `10/1/2025` the models used are:
        - `llm_model`: Aya Expase 8b
        - `backup_llm_model`: Aya 23 8b
        - `advanced`: Aya Expanse 32b

- Formats the input text using the `format_text` function.
- Prepares an `errors` list to track issues.


###### Validation Checks:
1. **Empty String Check**: Flags empty strings as errors.
2. **Language Detection**:
    - Identifies the language of the translated text.
    - Compares the detected language to the target `language_code`.
3. **Correctness Check**:
    - Uses prompts like `is_right_translation` to validate translation accuracy.
    - If incorrect, regenerates the translation using `backup_llm_model`.
4. **Mixed Language Handling**:
    - Checks for mixed-language content.
    - Extracts valid translations or regenerates using `backup_llm_model`.
5. **Unsupported Language**:
    - Handles unsupported or incorrect languages by regenerating translations with `backup_llm_model`.

###### Final Results:
- Returns `False` and the text if issues persist.
- Returns `True` and the refined text if validation succeeds.
