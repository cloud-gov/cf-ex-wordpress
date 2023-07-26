# cloud.gov PHP Example Application:  WordPress

This is an example application which can be run on cloud.gov using the CloudFoundry [PHP buildpack](http://docs.cloudfoundry.org/buildpacks/php/index.html).

This is an out-of-the-box implementation of WordPress. It's an example of how common PHP applications can easily be run on cloud.gov

1. [Installation](#installation)
1. [Administering your WordPress site](#administering-your-wordpress-site)
1. [Full example setup.json file](#full-example-setupjson-file)
1. [Recommendations](#recommendations)

## Installation

1. Clone this repo.

    ```bash
    git clone https://github.com/18F/cf-ex-wordpress.git cf-ex-wordpress
    cd cf-ex-wordpress
    ```

1. Create a service instance of a MySQL Database:

    ```bash
    # note: if this is for a production environment, use one of the plans with `-redundant` in the plan name for better availability
    # run `cf marketplace -s aws-rds` to see available database plans
    cf create-service aws-rds micro-mysql mysql-db
    ```

    See the [cloud.gov website page on database services.](https://cloud.gov/docs/services/relational-database/) for more information.

1. Create a service instance of S3 storage:

    ```bash
    # run `cf marketplace -s s3` to see available S3 plans
    cf create-service s3 basic-public s3-storage
    ```

    **Note**: cloud.gov does not have persistent local storage so you'll need to rely on S3 for storing any files uploaded to WordPress. Sandbox accounts cannot create S3 storage services. Consider upgrading to a prototyping package if you need to do this.

    [See the cloud.gov website page on S3 services for more information.](https://cloud.gov/docs/services/s3/)

1. Copy the example `manifest.yml.example` to `manifest.yml`. Edit the `manifest.yml` file:

    - Change the `name` and `host` attributes to something unique for your site.
    - Under `services:` change
      - `mysql-db` to the name of your MySQL service you created in Step 2.
      - `s3-storage` to the name of your S3 service you created in Step 3. Or delete this line if you're not using S3.
    - The memory and disk allocations in the example `manifest.yml` file should be [sufficient for WordPress](https://developer.wordpress.org/apis/wp-config-php/#increasing-memory-allocated-to-php) but may need to be adjusted depending on your specific needs.

1. Copy the example `setup.json.example` to `setup.json`. Edit the `setup.json` file for your specific WordPress site information, plugins you want installed, and themes.

    - **NOTE:** The example includes a set of plugins that will be used to attach to your previously created S3 storage so you can store media uploads, like pictures, for your WordPress site. If you do not use these plugins, every time you deploy, uploaded files will be lost.
    - See: [Setup JSON](#full-example-setupjson-file) for more information about the format of this file

1. Deploy the app with a no start command:

    ```bash
    cf push --no-start
    ```

    This will download and install WordPress, configure it to use your MySQL service, and install all your plugins and themes but will not start the application on cloud.gov.

1. Copy the example `setup.sh.example` to `setup.sh`.
1. Update `setup.sh` and replace the placeholder `YOUR-KEY` with the values from the [WordPress Secret Key Generator](https://api.wordpress.org/secret-key/1.1/salt/). Make sure to `chomd +x` the file, and then run it and pass in the name of your app: `./setup.sh mywordpress`. This will set these values as environmental values in the cloud.gov environment. **Note - Make sure to include the leading and closing `'` characters to avoid errors escaping special characters**.

1. Push the Wordpress application to CloudFoundry:

    ```bash
    cf push
    ```

    This will push the files in this repository to the platform (around 25k), including the buildpack extension we've adapted from the Cloud Foundry project. The server downloads and runs the [PHP buildpack](http://docs.cloudfoundry.org/buildpacks/php/index.html) which installs HTTPD and PHP. The buildpack sees the extension which installs [WP-CLI](http://wp-cli.org/), reads your `setup.json`, and installs and configures WordPress with any plugins or themes you have defined. Then it copies the `wp-config.php` file to replace the default from WordPress. Once all that is finished, the platform starts the application. Now you have a WordPress site.

    You should see output like this in your terminal:

    ```shell
    App started


    OK

    App mywordpress was started using this command `$HOME/.bp/bin/start`

    Showing health and status for app mywordpress in org sandbox-gsa / space your.name as your.name@agency.gov...
    OK

    requested state: started
    instances: 1/1
    usage: 128M x 1 instances
    urls: my-special-wordpress.app.cloud.gov
    last uploaded: Tue Sep 26 22:21:49 UTC 2017
    stack: cflinuxfs4
    buildpack: https://github.com/cloudfoundry/php-buildpack
    ```

    If you go to the URL listed under `urls` you should see a fresh WordPress site.

1. Verify S3 connection:

    This demo uses the [Human Made S3 Uploads plugin](https://github.com/humanmade/S3-Uploads), which automatically uploads files from your WordPress install to S3 and rewrites the URLs for you. The app requires no configuration. The access keys, secret key, and bucket name are stored in the environment configuration and read by the plugin on start.

    ```shell
    cf run-task mywordpress "php/bin/php htdocs/wp-cli.phar s3-uploads verify --path='/home/vcap/app/htdocs/'"
    ```

    To see that the task ran, run `cf logs APP_NAME --recent` and you should see a line that says:

    ```shell
    OUT Success: Looks like your configuration is correct.
    ```

1. Log in and test:

    To test everything is correct, log in to your WordPress site with the credentials in your `setup.json` file. You should be able to do any admin activities including creating a new post and uploading a media file to it.

## Administering your WordPress site

This example app uses `wp-cli` to install and configure WordPress based on the data in your `setup.json` file. If you want to further customize your installation you can edit the `.extensions/wordpress/extension.py` file in this repo or use continuous integration to run more `wp-cli` commands after the basic installer runs.

### Basic site options

The `site_info` section of the `setup.json` file is required and supplies basic information the Cloud Foundry process needs to set up your WordPress site. It looks like this by default:

```json
{
  "site_info": {
    "url": "https://mysite.app.cloud.gov",
    "title": "My new site",
    "admin_user": "admin",
    "admin_password": "CHANGEME",
    "admin_email": "my.email@example.com"
  }
}
```

Make sure you change these values, especially `url` and `title` to something specific to your app. At this time, these are the only options managed by the build process.

### Updating WordPress

By default, this package will install the latest version of WordPress. To update WordPress or pick up a new version of the PHP builpack, [run `cf restage APP_NAME`](https://cloud.gov/docs/getting-started/app-maintenance/). cloud.gov will install a fresh copy of WordPress Core each time you `push` or `restage`. We **do not recommend** using the wp-admin interface to manage updates to your site.

If you want to pin your Core installation to a specific version of WordPress, add `"wordpress_version": VERSION_NUMBER` on a line above the `site_info` section.

```json
{
  "wordpress_version": "4.8.2",
  "site_info": {
  }
}
```

**Note: We recommend running the latest stable version of WordPress on production sites.** The latest version typically contains important security updates. If you pin the WordPress version, you will need to manually increment this value to upgrade your install. Make sure you follow [the update schedule on wordpress.org](https://wordpress.org/news/category/releases/) to keep up with important security and maintenance releases.

### Themes and plugins

The Cloud Foundry platform builds apps with ephemeral local storage. This means any changes made to local files on your app will get deleted whenever you `push` or `restage` the app. Make sure your plugins and themes remain installed by installing them through the `plugins` and `themes` sections of the `setup.json` file.

For plugins or themes you'd normally be able to install from the admin interface, you can list them by name and the version that you want installed. For anything not available through WordPress directly, provide a URL to a ZIP file. For example, if your site's theme is one you've custom-developed, you can host it on GitHub and use the "Download ZIP" link to install it.

```json
"plugins": [
  {
    "url": "https://github.com/humanmade/S3-Uploads/archive/v1.1.0.zip"
  },
  {
    "name": "akismet",
    "version": "4.0"
  },
  {
    "name": "hello-dolly"
  }
],
"themes": [
    {
      "name": "create",
      "version": "1.3"
    }
  ]
```

In the sample `setup.json` file you see three plugins installed by default. One from GitHub and two from WordPress, one of which is pinned to a specific version. As with WordPress Core, if you pin the version, make sure to watch for and install updates that contain security fixes.

### Running WP-CLI commands

We recommend using Cloud Foundry's "tasks" to run `wp-cli` commands. To do this, make sure to give the full path for both PHP and the `wp-cli.phar` file and specify the WordPress path relative to the `app` directory. Here's how you'd run `wp core version` on your cloud.gov container:

```bash
cf run-task APP_NAME "php/bin/php htdocs/wp-cli.phar core version --path='htdocs/'"
```

That should print something like:

```shell
Creating task for app APP_NAME in org ORG_NAME / space SPACE_NAME as USER_NAME...
OK

Task has been submitted successfully for execution.
task name:   98680974
task id:     30
```

Run `cf logs APP_NAME --recent` to see the results and look for the `task name` to see the results. The task will create a container, run your command and then destroy the container after the task exits.

```shell
2017-09-27T10:54:44.36-0600 [APP/TASK/98680974/0] OUT Creating container
2017-09-27T10:54:44.81-0600 [APP/TASK/98680974/0] OUT Successfully created container
2017-09-27T10:54:51.50-0600 [APP/TASK/98680974/0] OUT 4.8.2
2017-09-27T10:54:51.52-0600 [APP/TASK/98680974/0] OUT Stopping instance 13abb9c4-23fe-4fc6-8b72-dc6676be26b8
2017-09-27T10:54:51.51-0600 [APP/TASK/98680974/0] OUT Exit status 0
2017-09-27T10:54:51.52-0600 [APP/TASK/98680974/0] OUT Destroying container
2017-09-27T10:54:52.92-0600 [APP/TASK/98680974/0] OUT Successfully destroyed container
```

Consider using [continuous integration](https://cloud.gov/docs/apps/continuous-deployment/) to run any tasks that should be run every time you `push` or `restage` your app or that you want to run at regular time intervals.

## Full example setup.json file

```json
{
  "wordpress_version": "4.4",
  "site_info": {
    "url": "https://CHANGEME.app.cloud.gov",
    "title": "My new site",
    "admin_user": "admin",
    "admin_password": "CHANGEME",
    "admin_email": "my.email@example.com"
  },
  "plugins": [
    {
      "name": "akismet",
      "version": "4.0"
    },
    {
      "url": "https://example.org/my-great-plugin-0.1.zip"
    }
  ],
  "themes": [
    {
      "name": "create",
      "version": "1.3"
    }
  ]
}
```

## Recommendations

1. You will probably want to connect your app to some kind of SMTP service to send transactional emails like password resets.
1. The S3 Uploads plugin rewrites the URLs used by WordPress but does not flush the rewrite rules table automatically. To get around this, you can [run a task](https://cloud.gov/docs/getting-started/one-off-tasks/) to flush the rewrite rules after every `cf push` of your app. You can also automate those tasks by using [continuous integration](https://cloud.gov/docs/apps/continuous-deployment/).

## License

See [LICENSE](LICENSE.md) for license details.
