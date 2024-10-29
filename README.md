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

### 1. Middleware
The app features `CacheUpdateMiddleware`, which activates during site load to optimize performance and manage requests effectively. This system works by updating the `cache_update_index` each time admin makes changes in the backend. When a user visits the site, a request is made to retrieve the current `cache_update_index`. If the saved index in the user's browser matches the current one, no action is taken; however, if the indices differ, the cache is refreshed.