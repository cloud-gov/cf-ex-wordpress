# cloud.gov PHP Example Application:  WordPress

This is an example application which can be run on cloud.gov using the CloudFoundry [PHP buildpack](http://docs.cloudfoundry.org/buildpacks/php/index.html).

This is an out-of-the-box implementation of WordPress. It's an example of how common PHP applications can easily be run on cloud.gov

1. [Installation](#installation)
1. [Administering your WordPress site](#administering-your-wordpress-site)
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
    # run `cf marketplace -e aws-rds` to see available database plans
    cf create-service aws-rds micro-mysql mysql-db
    ```

    See the [cloud.gov website page on database services.](https://cloud.gov/docs/services/relational-database/) for more information.

1. Create a service instance of S3 storage:

    ```bash
    # run `cf marketplace -e s3` to see available S3 plans
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

1. Deploy the app with a no start command:

    ```bash
    cf push --no-start
    ```

    This will download and install WordPress, configure it to use your MySQL service, and install all your plugins and themes but will not start the application on cloud.gov.

1. Copy the example `setup.sh.example` to `setup.sh` and then:
1. Update `setup.sh` and replace the placeholder `YOUR-KEY` with the values from the [WordPress Secret Key Generator](https://api.wordpress.org/secret-key/1.1/salt/).
1. Update `setup.sh` to set the values that will be used when installing your site:

    - `SITE_NAME`: name for your Wordpress site
    - `SITE_URL`: URL for your website, which should either be the URL ending in `app.cloud.gov` printed by CloudFoundry after `cf push` or your custom agency domain (e.g. `agency.gov`)
    - `ACCOUNT_NAME`: name for your site's admin user account
    - `ACCOUNT_EMAIL`: email address for your admin user account
    - `ACCOUNT_PASS`: password for your site's admin user account

1. Make sure to `chmod +x` the file:

    ```bash
    chmod +x setup.sh
    ```

1. Run it and pass in the name of your app that you set in `manifest.yml`:

    ```bash
    ./setup.sh mywordpress
    ```

    This will set these values as environmental values in the cloud.gov environment. **Note - Make sure to include the leading and closing `'` characters to avoid errors escaping special characters**.

1. Push the Wordpress application to CloudFoundry:

    ```bash
    cf push
    ```

    On `cf push`:

    - The server downloads and runs the [PHP buildpack](http://docs.cloudfoundry.org/buildpacks/php/index.html) which installs HTTPD and PHP
    - The buildpack includes the `composer` extension, so it sees `compser.json` and installs the defined packages from there, including Wordpress, the WP CLI, and some plugins/themes
    - [A custom script](./scripts/bootstrap.sh) copies the Wordpress files installed by `composer` into the web root for the application and installs Wordpress using the environment variables configured in `setup.sh`
    - The platform starts the application

    Now you have a WordPress site. You should see output like this in your terminal:

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
    # for CF CLI v7
    cf run-task mywordpress "wp s3-uploads verify --path='/home/vcap/app/htdocs/'"
    # for CF CLI v8
    cf run-task mywordpress --command "wp s3-uploads verify --path='/home/vcap/app/htdocs/'"
    ```

    To see that the task ran, run `cf logs APP_NAME --recent` and you should see a line that says:

    ```shell
    OUT Success: Looks like your configuration is correct.
    ```

1. Log in and test:

    To test everything is correct, log in to your WordPress site with the credentials you specified when running `wp core install` in the previous step. You should be able to do any admin activities including creating a new post and uploading a media file to it.

## Administering your WordPress site

### Updating WordPress

By default, this example will the latest version of WordPress specified in `composer.json` and `composer.lock`. To update WordPress or pick up a new version of the PHP builpack, run:

```shell
composer update johnpbloch/wordpress
```

Then, re-push your application:

```shell
cf push
```

We **do not recommend** using the wp-admin interface to manage updates to your site.

**Note: We recommend running the latest stable version of WordPress on production sites.** The latest version typically contains important security updates. If you pin the WordPress version, you will need to manually increment this value to upgrade your install. Make sure you follow [the update schedule on wordpress.org](https://wordpress.org/news/category/releases/) to keep up with important security and maintenance releases.

### Themes and plugins

The Cloud Foundry platform builds apps with ephemeral local storage. This means any changes made to local files on your app will get deleted whenever you `push` or `restage` the app. Make sure your plugins and themes remain installed by installing them through the `composer.json` file using [`composer require`](https://getcomposer.org/doc/03-cli.md#require-r).

By default, these plugins/themes are included:

- [`S3-Uploads`](https://github.com/humanmade/S3-Uploads): Integrates with S3 for storing uploaded site files
- `Akismet`: Default spam protection plugin for Wordpress
- `Create` Wordpress theme

For plugins or themes you'd normally be able to install from the admin interface, you can list them by name and the version that you want installed. For anything not available through WordPress directly, you can [use composer to require packages from GitHub](https://getcomposer.org/doc/05-repositories.md#vcs). For example, if your site's theme is one you've custom-developed, you can follow those instructions to require it via `composer.json`.

As with WordPress Core, make sure to watch for and install updates for the plugins/themes that contain security fixes.

### Running WP-CLI commands

We recommend using Cloud Foundry's "tasks" to run `wp-cli` commands. To do this, make sure to specify the WordPress path relative to the `app` directory. Here's how you would run `wp core version` on your cloud.gov container:

```bash
# for CF CLI v7
cf run-task APP_NAME "wp core version --path='/home/vcap/app/htdocs/'"
# for CF CLI v8
cf run-task APP_NAME --command "wp core version --path='/home/vcap/app/htdocs/'"
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
2017-09-27T10:54:51.50-0600 [APP/TASK/98680974/0] OUT 6.2.2
2017-09-27T10:54:51.52-0600 [APP/TASK/98680974/0] OUT Stopping instance 13abb9c4-23fe-4fc6-8b72-dc6676be26b8
2017-09-27T10:54:51.51-0600 [APP/TASK/98680974/0] OUT Exit status 0
2017-09-27T10:54:51.52-0600 [APP/TASK/98680974/0] OUT Destroying container
2017-09-27T10:54:52.92-0600 [APP/TASK/98680974/0] OUT Successfully destroyed container
```

Consider using [continuous integration](https://cloud.gov/docs/apps/continuous-deployment/) to run any tasks that should be run every time you `push` or `restage` your app or that you want to run at regular time intervals.

## Recommendations

1. You will probably want to connect your app to some kind of SMTP service to send transactional emails like password resets.
1. The S3 Uploads plugin rewrites the URLs used by WordPress but does not flush the rewrite rules table automatically. To get around this, you can [run a task](https://cloud.gov/docs/getting-started/one-off-tasks/) to flush the rewrite rules after every `cf push` of your app. You can also automate those tasks by using [continuous integration](https://cloud.gov/docs/apps/continuous-deployment/).

## License

See [LICENSE](LICENSE.md) for license details.
