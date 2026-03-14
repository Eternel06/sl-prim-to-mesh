string BASE_URL = "https://sl-prim-to-mesh-production.up.railway.app";

string primTypeToStr(integer t) {
    if (t == PRIM_TYPE_BOX)      return "BOX";
    if (t == PRIM_TYPE_CYLINDER) return "CYLINDER";
    if (t == PRIM_TYPE_SPHERE)   return "SPHERE";
    if (t == PRIM_TYPE_TORUS)    return "TORUS";
    if (t == PRIM_TYPE_TUBE)     return "TUBE";
    if (t == PRIM_TYPE_RING)     return "RING";
    if (t == PRIM_TYPE_PRISM)    return "PRISM";
    return "BOX";
}

string fv(float f) {
    integer cents = (integer)llRound(f * 100.0);
    integer whole = cents / 100;
    integer dec = cents % 100;
    if (dec < 0) dec = -dec;
    if (dec == 0) return (string)whole;
    if (dec % 10 == 0) return (string)whole + "." + (string)(dec/10);
    string d = (string)dec;
    if (dec < 10) d = "0" + d;
    return (string)whole + "." + d;
}

string fv4(float f) {
    integer thou = (integer)llRound(f * 10000.0);
    integer whole = thou / 10000;
    integer dec = thou % 10000;
    if (dec < 0) dec = -dec;
    if (dec == 0) return (string)whole;
    string d = (string)dec;
    while (llStringLength(d) < 4) d = "0" + d;
    while (llStringLength(d) > 1 && llGetSubString(d,-1,-1) == "0")
        d = llGetSubString(d, 0, -2);
    return (string)whole + "." + d;
}

string gSessionID = "";
integer gCurrentPrim = 1;
integer gTotalPrims = 0;
integer gChunkSize = 3;
key gRequestID;
integer gState = 0;

string buildChunk(integer from, integer to) {
    string json = "[";
    integer i;
    for (i = from; i <= to; i++) {
        vector pos;
        vector size;
        rotation rot;
        integer primType;
        float hollow;
        float path_cut_begin;
        float path_cut_end;
        float taper_x;
        float taper_y;
        vector color;
        float alpha;

        list typeData;
        if (gTotalPrims == 1) {
            pos      = llGetPos();
            size     = llGetScale();
            rot      = llGetRot();
            typeData = llGetPrimitiveParams([PRIM_TYPE]);
            list colorData = llGetPrimitiveParams([PRIM_COLOR, 0]);
            color = llList2Vector(colorData, 0);
            alpha = llList2Float(colorData, 1);
        } else {
            list xform = llGetLinkPrimitiveParams(i,
                [PRIM_POSITION, PRIM_ROTATION, PRIM_SIZE]);
            pos  = llList2Vector(xform, 0);
            rot  = llList2Rot(xform, 1);
            size = llList2Vector(xform, 2);
            typeData = llGetLinkPrimitiveParams(i, [PRIM_TYPE]);
            list colorData = llGetLinkPrimitiveParams(i, [PRIM_COLOR, 0]);
            color = llList2Vector(colorData, 0);
            alpha = llList2Float(colorData, 1);
        }

        primType       = llList2Integer(typeData, 0);
        path_cut_begin = llList2Float(typeData, 1);
        path_cut_end   = llList2Float(typeData, 2);
        hollow         = llList2Float(typeData, 3) / 100.0;
        vector taperVec = llList2Vector(typeData, 5);
        taper_x = taperVec.x;
        taper_y = taperVec.y;

        string entry = "{";
        entry += "\"type\":\"" + primTypeToStr(primType) + "\",";
        entry += "\"position\":[" + fv(pos.x) + "," + fv(pos.y) + "," + fv(pos.z) + "],";
        entry += "\"size\":[" + fv(size.x) + "," + fv(size.y) + "," + fv(size.z) + "],";
        entry += "\"rotation\":[" + fv4(rot.x) + "," + fv4(rot.y) + "," + fv4(rot.z) + "," + fv4(rot.s) + "],";
        entry += "\"hollow\":" + fv4(hollow) + ",";
        entry += "\"path_cut_begin\":" + fv4(path_cut_begin) + ",";
        entry += "\"path_cut_end\":" + fv4(path_cut_end) + ",";
        entry += "\"taper_x\":" + fv4(taper_x) + ",";
        entry += "\"taper_y\":" + fv4(taper_y) + ",";
        entry += "\"color\":[" + fv4(color.x) + "," + fv4(color.y) + "," + fv4(color.z) + "],";
        entry += "\"alpha\":" + fv4(alpha);
        entry += "}";
        if (i < to) entry += ",";
        json += entry;
    }
    json += "]";
    return json;
}

sendChunk() {
    integer to = gCurrentPrim + gChunkSize - 1;
    if (to > gTotalPrims) to = gTotalPrims;
    llOwnerSay("Sending prims " + (string)gCurrentPrim + " to "
               + (string)to + " of " + (string)gTotalPrims + "...");
    string chunk = buildChunk(gCurrentPrim, to);
    string encoded = llEscapeURL(chunk);
    string url = BASE_URL + "/chunk?sid=" + gSessionID + "&data=" + encoded;
    gRequestID = llHTTPRequest(url,
        [HTTP_METHOD, "GET", HTTP_VERIFY_CERT, FALSE], "");
    gCurrentPrim = to + 1;
}

default {
    state_entry() {
        llOwnerSay("Prim to Mesh v4 ready! Prims: "
                   + (string)llGetNumberOfPrims());
    }

    touch_start(integer nd) {
        if (llDetectedKey(0) != llGetOwner()) return;
        gTotalPrims  = llGetNumberOfPrims();
        gCurrentPrim = 1;
        gState       = 1;
        llOwnerSay("Starting conversion of "
                   + (string)gTotalPrims + " prims...");
        gRequestID = llHTTPRequest(
            BASE_URL + "/start",
            [HTTP_METHOD, "GET", HTTP_VERIFY_CERT, FALSE], "");
    }

    http_response(key request_id, integer status, list metadata, string body) {
        if (request_id != gRequestID) return;
        if (status != 200) {
            llOwnerSay("Error " + (string)status + ": " + body);
            gState = 0;
            return;
        }
        if (gState == 1) {
            gSessionID = body;
            llOwnerSay("Session started!");
            gState = 2;
            sendChunk();
        } else if (gState == 2) {
            if (gCurrentPrim <= gTotalPrims) {
                sendChunk();
            } else {
                gState = 3;
                llOwnerSay("Generating mesh...");
                gRequestID = llHTTPRequest(
                    BASE_URL + "/generate?sid=" + gSessionID,
                    [HTTP_METHOD, "GET", HTTP_VERIFY_CERT, FALSE], "");
            }
        } else if (gState == 3) {
            gState = 0;
            llOwnerSay("Done! Opening browser...");
            llLoadURL(llGetOwner(),
                "Click to download your .dae mesh file!", body);
        }
    }
}
