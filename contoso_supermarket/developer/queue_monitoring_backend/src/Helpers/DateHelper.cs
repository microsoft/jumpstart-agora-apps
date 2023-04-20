using System;

namespace Contoso.Backend.Data.Helpers
{
    public static class DateHelper
    {
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
