/**
* Determines if the current document is in a frameset
* and if not opens using index.html as target of frameset.
*/
function openFrameSet() 
{
	if (parent != null && parent.frames.length == 0) {
		var s = window.location.toString();
		
		// see if we are dealing with a specific 
		// class, package, pipelet, or group file
		var translate = false;
		var idx = s.indexOf("class.");
		if (idx < 0) {
		    idx = s.indexOf("class_");
		} else {
			translate = true;
		}
		
		if (idx < 0) {
		    idx = s.indexOf("package.");
		    if (idx > 0) {
		    	translate = true;
		    }
		}
		if (idx < 0) {
		    idx = s.indexOf("package_");
		}
		if (idx < 0) {
		    idx = s.indexOf("pipelet.");
		}
		if (idx < 0) {
		    idx = s.indexOf("group.");
		}
		
		if (translate) {
			var idx = s.indexOf('.');
			while (idx > 0)
			{
				if (idx != s.lastIndexOf('.'))
				{
					s = s.replace('.','_');
					idx = s.indexOf('.');
				}
				else
				{
					idx = 0;
				}
			}
		}
		
		// if we have a target, update url
		if (idx >= 0) {
		   s = s.substring(idx);
		   window.location = "../index.html?target=" + s;	   

		} else {
		   window.location = "../index.html";
		}
 	}
}

/**
* Determines if the frame should be updated using the 
* specified target.
*/
function updateFrame(theFrame) {

	// get the parameters from the request
	var s = window.location.toString(); 
	var idx = s.indexOf("target=");
	if (idx > 0) {
		idx = idx + 7;
		s = s.substring(idx);
		var frmSrc = theFrame.src;

		

		// only update the frame if the current src is overview
		if (frmSrc.indexOf("api/overview.html") >= 0 && s.indexOf("class_") == 0) {
			//calling this will generate an event
			theFrame.src = "api/" + s; 
		}
		
		// only update the frame if the current src is overview
		if (frmSrc.indexOf("api/overview.html") >= 0 && s.indexOf("class.") == 0) {
			//calling this will generate an event
			var idx = s.indexOf('.');
			while (idx > 0)
			{
				if (idx != s.lastIndexOf('.'))
				{
					s = s.replace('.','_');
					idx = s.indexOf('.');
				}
				else
				{
					idx = 0;
				}
			}
				
			theFrame.src = "api/" + s; 
		}
		
		// only update the frame if the current src is overview
		if (frmSrc.indexOf("api/overview.html") >= 0 && s.indexOf("pipelet.") == 0) {
			//calling this will generate an event
			theFrame.src = "api/" + s; 
		}

		// only update frame if currently class list
		if (frmSrc.indexOf("api/classList.html") >= 0 && s.indexOf("package_") == 0) {
			//calling this will generate an event
			theFrame.src = "api/" + s; 
		}

		// only update frame if currently class list
		if (frmSrc.indexOf("api/classList.html") >= 0 && s.indexOf("package.") == 0) {
			//calling this will generate an event
			var idx = s.indexOf('.');
			while (idx > 0)
			{
				if (idx != s.lastIndexOf('.'))
				{
					s = s.replace('.','_');
					idx = s.indexOf('.');
				}
				else
				{
					idx = 0;
				}
			}
			theFrame.src = "api/" + s; 
		}

		// only update frame if currently class list
		if (frmSrc.indexOf("api/pipeletList.html") >= 0 && s.indexOf("group.") == 0) {
			//calling this will generate an event
			theFrame.src = "api/" + s; 
		}
	}
}