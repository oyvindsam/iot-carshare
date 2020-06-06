function checkDate()
{
    var startDate = new Date(document.getElementById("bookingstarttime").value);
    var endDate = new Date(document.getElementById("bookingendtime").value);
    if(startDate > endDate)
    {
        alert("Please enter end date time which is greater than the start date and time!!");
        return false;
    }
}