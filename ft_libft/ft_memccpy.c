/* ************************************************************************** */
/*                                                                            */
/*                                                        :::      ::::::::   */
/*   ft_memccpy.c                                       :+:      :+:    :+:   */
/*                                                    +:+ +:+         +:+     */
/*   By: gcyril <marvin@42.fr>                      +#+  +:+       +#+        */
/*                                                +#+#+#+#+#+   +#+           */
/*   Created: 2019/10/20 20:20:35 by gcyril            #+#    #+#             */
/*   Updated: 2019/11/05 21:01:38 by gcyril           ###   ########.fr       */
/*                                                                            */
/* ************************************************************************** */

#include "libft.h"

void	*ft_memccpy(void *dest, const void *src, int c, size_t size)
{
	size_t			i;
	unsigned char	*mysrc;
	unsigned char	*mydest;

	i = 0;
	mysrc = (unsigned char *)src;
	mydest = (unsigned char *)dest;
	while (i < size)
	{
		mydest[i] = mysrc[i];
		if (mysrc[i] == (unsigned char)c)
			return (dest + i + 1);
		i++;
	}
	return (NULL);
}
