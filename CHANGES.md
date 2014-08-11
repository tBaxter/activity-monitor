# Activity Monitor Change Log

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
