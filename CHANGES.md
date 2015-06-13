# Activity Monitor Change Log

### 0.11.3
* Clean build, with registration.

### 0.11.2
* Clean build attempt

### 0.11.1
* Cleanup on travis.yml and test settings.

### 0.11.0 -- 6.13.2015
* Added some tests

### 0.10.9 -- 9.22.2014
* Ensure valid user object before saving.

### 0.10.8 -- 8.27.2014
* Fixed shoddy date comparison in current_item. For real.

### 0.10.7
* Fixed shoddy date comparison in current_item.

### 0.10.6
* Removed 'showing current day', replaced by current_item in grouper.

### 0.10.5 -- 8-26-2014
* Corrected view next and previous definitions

### 0.10.4
* added "showing current day" to context

### 0.10.3
* Passing back next and previous days in view, too.

### 0.10.2
* Passing back next and previous days in view, too.

### 0.10.1
* Small change to keep date and url tag happy together.

### 0.10.0
* Added paginate by day template tag

### 0.9.2
* minor import refactoring for cleanliness

### 0.9.1
* Updates for Django 1.7 app registry.

### 0.9.0
* Activities for today gets rolling 24 hours instead of resetting at midnight
* Added get_activity_count simple tag to get activities for a given date (defaults to today).

### 0.8.1
* Forgot to follow content_object

### 0.8.0 -- 8-13-2014
* Modified template tag to take an optional grouped activity as created by utils.group_activity
* Revised get_image helper to look for target.image, but only if get_image found nothing.

### 0.7.8
Small bug fixes for image resolution.

### 0.7.6
Resolve image objects to just get image. If the full image object is desired, follow the relationship through content_object.

### 0.7.5
Clarify image vs get_image()

### 0.7.4
Wrapped in try/except for your safety.

### 0.7.3
Simpler checking for image

### 0.7.2
Object getting order was backwards. Get locally first, then follow to content_object.

### 0.7.1
get_image() follows GFKs to their object, and requires get_image to be defined on the related model to avoid unwanted and extraneous images.

### 0.7.0
Added get_image to activities, extracting from the related content_object

### 0.6.0
More options, more docs.

### 0.5.0
Added including and excluding specific content types to template tag.

### 0.4.4
Standardized on 'actions'.

### 0.4.3
Last seen continues to cause problems.

### 0.4.1
Resolved some last seen conflicts

### 0.4
Improved custom templates, and activity's related content object is now passed to custom templates.

### 0.3.2
Setup.py fix

### 0.3.1
Added example custom template

### 0.3
Added ability to show arbitrary template snippet output for given activity.

### 0.2.1
Grouped output for template tags

### 0.2
Better template tags, more cleanup

### 0.1
* Decrufted very old app to prepare for more public consumption
