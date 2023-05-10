namespace Contoso.Backend.Data.Helpers
{
    public static class DateHelper
    {
        /// <summary>
        /// Appends the time zone to a DateTimeOffset object.
        /// </summary>
        /// <param name="dateTime">The DateTimeOffset object to append the time zone to.</param>
        /// <param name="timeZone">The time zone to append.</param>
        /// <returns>A DateTimeOffset object with the appended time zone.</returns>
        public static DateTimeOffset AppendTimeZone(this DateTimeOffset dateTime, string? timeZone)
        {
            DateTimeOffset ret;
            if (timeZone == null)
            {
                return dateTime;
            }
            else
            {
                var tz = TimeZoneInfo.FindSystemTimeZoneById(timeZone);
                ret = new DateTimeOffset(dateTime.Ticks, tz.GetUtcOffset(dateTime));
            }
            return ret;
        }

        /// <summary>
        /// Converts a UTC DateTimeOffset object to a specified time zone.
        /// </summary>
        /// <param name="utcDateTimeOffset">The UTC DateTimeOffset object to convert.</param>
        /// <param name="timeZone">The time zone to convert to.</param>
        /// <returns>A DateTimeOffset object converted to the specified time zone.</returns>
        public static DateTimeOffset ConvertTimeZone(this DateTimeOffset utcDateTimeOffset, string? timeZone)
        {
            DateTimeOffset ret;
            if (timeZone == null)
            {
                return utcDateTimeOffset;
            }
            else
            {
                var tz = TimeZoneInfo.FindSystemTimeZoneById(timeZone);
                TimeSpan nzOffsetDifference = tz.GetUtcOffset(utcDateTimeOffset);
                ret = new DateTimeOffset(utcDateTimeOffset.DateTime.Add(nzOffsetDifference), nzOffsetDifference);
            }
            return ret;
        }
    }
}